# cogs/manual.py - the bot's own documentation, searchable by humans and by the AI.
#
# Source of truth is docs/manual.md in the repo root. Sections are split on
# "## " headings. Any number of hidden keyword comments may appear inside a
# section and they are all merged:
#
#     ## Moderation commands
#     <!-- kw: warn, kick, ban -->
#     Body text the user and the AI can read.
#
# lookup() scores a query against those keywords plus a little of the section
# title, so "how do i ban someone" lands on the moderation section.

import pathlib
import re

import discord
from discord import app_commands
from discord.ext import commands

from cogs.utils import get_setting

MANUAL_PATH = pathlib.Path(__file__).resolve().parent.parent / "docs" / "manual.md"

# Questions shaped like someone wanting instructions. These get the manual
# injected. Questions that merely match a topic do not: "what animal commands
# are there" is answerable, but the AI should not pretend it is being taught.
_HOWTO = re.compile(
    r"\b(how (do|to|can|does|did|would)|what('?s| is) the (command|way|command to)|"
    r"whats the|where (do|can) i|who can|which command|"
    r"is there a (command|way)|do you (have|support|know))\b",
    re.IGNORECASE,
)

# Topic-shaped questions. These also get the manual, because the honest answer
# comes from it rather than from the model's memory.
_TOPIC = re.compile(
    r"\b(what|which|list|show|tell me|explain|are there|does it|is it)\b",
    re.IGNORECASE,
)

# Questions about this specific server rather than the bot in general.
_LOCAL = re.compile(
    r"\b(here|this server|our server|on (here|this server)|in (here|this server))\b",
    re.IGNORECASE,
)

# Score needed to be worth sending to the model.
_MIN_SCORE = 4
_MAX_CONTEXT_CHARS = 3000


def _load_sections() -> list[dict]:
    """Parse the manual into [{title, keywords, body}]. Empty list if missing."""
    if not MANUAL_PATH.exists():
        return []
    text = MANUAL_PATH.read_text(encoding="utf-8")
    sections = []
    for part in re.split(r"^## ", text, flags=re.MULTILINE)[1:]:
        lines = part.splitlines()
        body = "\n".join(lines[1:]).strip()
        keywords: list[str] = []
        for m in re.finditer(r"<!--\s*kw:\s*(.*?)\s*-->", body, re.DOTALL):
            keywords += [k.strip().lower() for k in m.group(1).split(",") if k.strip()]
        body = re.sub(r"<!--\s*kw:\s*.*?\s*-->", "", body, flags=re.DOTALL).strip()
        seen: set[str] = set()
        keywords = [k for k in keywords if not (k in seen or seen.add(k))]
        sections.append({"title": lines[0].strip(), "keywords": keywords, "body": body})
    return sections


SECTIONS: list[dict] = _load_sections()


# Words that carry no topic meaning. Without this, "the" matches every title
# that contains "The" and pushes unrelated sections over the score threshold.
_STOP = {
    "the", "and", "for", "with", "that", "this", "from", "are", "was", "you",
    "your", "youre", "have", "has", "had", "what", "whats", "how", "why", "when",
    "where", "which", "who", "can", "could", "would", "should", "does", "did",
    "about", "into", "there", "their", "them", "then", "than", "some", "someone",
    "somebody", "any", "all", "not", "but", "out", "off", "use", "using", "get",
    "got", "want", "need", "know", "like", "just", "one", "two", "way", "make",
    "made", "do", "doing", "done", "it", "its", "is", "am", "me", "my", "we",
    "work", "works", "working", "thing", "things", "stuff",
}


def _tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower())
            if len(w) > 2 and w not in _STOP}


def _lead(s: dict) -> str:
    """The section's own intro, without its `###` subsections.

    Subsection keywords are merged into the parent, and their shared words
    (command, response, user) would otherwise make the parent win everything.
    """
    body = s["body"]
    cut = body.find("\n### ")
    return body[:cut] if cut != -1 else body


def lookup(query: str, limit: int = 2) -> list[dict]:
    """Best matching sections for a query, strongest first.

    Keywords carry the weight. A section's own intro is only a weak tiebreaker,
    so a long intro cannot outrank a real keyword hit.
    """
    if not query.strip():
        return []
    q = query.lower()
    q_tokens = _tokens(q)
    scored = []
    for s in SECTIONS:
        score = 0
        for kw in s["keywords"]:
            if re.search(rf"\b{re.escape(kw)}\b", q):
                # Exact phrase hit inside the query. Strongest signal.
                score += 6 if " " in kw else 5
            elif kw in q_tokens:
                score += 2
            elif kw and any(tok.startswith(kw) for tok in q_tokens):
                # Plural or inflected form, e.g. "remind" for "reminders".
                # Strong enough to stand alone, but weaker than an exact hit.
                score += 4
        score += 4 * len(q_tokens & _tokens(s["title"]))
        score += min(len(q_tokens & _tokens(_lead(s))), 3)
        if score >= _MIN_SCORE:
            scored.append((score, s))
    scored.sort(key=lambda x: -x[0])
    return [s for _, s in scored[:limit]]


def is_bot_question(message_text: str) -> bool:
    """True when the message is the kind of thing the manual can answer."""
    if _HOWTO.search(message_text):
        return True
    if _TOPIC.search(message_text):
        return bool(lookup(message_text))
    return False


async def build_context(guild, message_text: str) -> str | None:
    """Reference text for the AI, or None when the manual is not the answer.

    Only bot-shaped questions get it. "roast me" matches the AI section by
    keyword but is not a question about the bot, so it stays a roast.
    Includes this server's live settings when the question is about the server.
    """
    if not is_bot_question(message_text):
        return None

    hits = lookup(message_text)
    if not hits:
        return None

    blocks = [f"Manual section '{h['title']}':\n{h['body']}" for h in hits]
    context = "\n\n".join(blocks)

    if _LOCAL.search(message_text) and guild is not None:
        facts = await _server_facts(guild)
        if facts:
            context += f"\n\nLive settings for {guild.name}:\n{facts}"

    return context[:_MAX_CONTEXT_CHARS]


async def _server_facts(guild) -> str:
    """Compact readout of this server's config, so the AI can answer specifics."""
    rows = [
        ("prefix", "prefix", None),
        ("automod_enabled", "automod on", bool),
        ("automod_action", "automod action", None),
        ("automod_mute_minutes", "automod mute minutes", None),
        ("antiraid_enabled", "antiraid on", bool),
        ("antiraid_threshold", "antiraid threshold", None),
        ("antiraid_seconds", "antiraid window seconds", None),
        ("antiraid_action", "antiraid action", None),
        ("warn_kick_threshold", "kick at warns", None),
        ("warn_ban_threshold", "ban at warns", None),
        ("warn_mute_threshold", "mute at warns", None),
        ("starboard_emoji", "starboard emoji", None),
        ("starboard_threshold", "starboard threshold", None),
        ("autorole_id", "autorole", None),
        ("jail_role_id", "jail role", None),
        ("jail_channel_id", "jail channel", None),
        ("deadchat_role_id", "deadchat ping role", None),
        ("deadchat_perm_role", "deadchat restricted to", None),
        ("log_mod_id", "mod log", None),
        ("log_message_id", "message log", None),
        ("log_member_id", "member log", None),
        ("log_server_id", "server log", None),
        ("welcome_channel_id", "welcome channel", None),
    ]
    out = []
    for key, label, caster in rows:
        v = await get_setting(guild.id, key)
        if v in (None, 0, ""):
            continue
        if caster is bool:
            out.append(f"{label}: {'yes' if v else 'no'}")
        elif key.endswith("_id"):
            obj = guild.get_role(v) if key.endswith("role_id") else guild.get_channel(v)
            out.append(f"{label}: {obj.mention if obj else f'not found ({v})'}")
        else:
            out.append(f"{label}: {v}")
    return "\n".join(out)


class Manual(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="manual", description="Look up how something works")
    @app_commands.describe(topic="What you want to know, e.g. jail, automod, warn")
    async def slash_manual(self, i: discord.Interaction, topic: str):
        hits = lookup(topic)
        if not hits:
            await i.response.send_message(
                "Nothing in the manual matches that. Try `/manualindex` for the list.",
                ephemeral=True)
            return
        h = hits[0]
        e = discord.Embed(title=h["title"], description=h["body"][:3900], color=0x5865F2)
        if len(hits) > 1:
            e.set_footer(text="Also matched: " + ", ".join(x["title"] for x in hits[1:]))
        await i.response.send_message(embed=e, ephemeral=False)

    @app_commands.command(name="manualindex", description="List every manual topic")
    async def slash_manual_index(self, i: discord.Interaction):
        e = discord.Embed(title="Manual topics", color=0x5865F2)
        e.description = "\n".join(
            f"**{s['title']}**\n`/manual {s['keywords'][0] if s['keywords'] else s['title']}`"
            for s in SECTIONS)
        await i.response.send_message(embed=e, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Manual(bot))
