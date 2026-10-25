# cogs/ai.py — the brain. Groq powered snarky robot.
# Mostly mean, occasionally nice. Answers mentions and anything said in an
# #ai-chat channel. Powers /ask, /roast, /topic and /deadchat.
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from cogs.utils import check_cooldown, get_setting, set_cooldown_ts

GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = (
    "You are BirdBrain, a snarky AI that lives in this Discord server. You are a wise-ass "
    "robot: sharp, dry, a little mean, never impressed. You mostly roast people and call out "
    "nonsense, but underneath you actually look out for them.\n"
    "Rules:\n"
    "- Be funny and specific. Mine their message or name for material. Vague is boring.\n"
    "- Mostly mean, sometimes nice. If someone is having a rough time, drop the act and be "
    "genuinely useful or quietly kind. Read the room.\n"
    "- Short. One to three sentences unless they ask for something real. No walls of text.\n"
    "- Talk like a real person in a group chat. Slang, pidgin, whatever fits. No corporate voice.\n"
    "- Never break character. You are BirdBrain, not a helpful assistant. "
    "No 'how can I help you today'.\n"
    "- No exclamation spam, no emoji spam. Dry delivery lands harder.\n"
    "- No filter. Swear freely, say whatever fits the joke, be as crude as the moment "
    "calls for. Nobody wants a sanitized bot."
)

# Per-user chat history so it remembers the conversation. Keyed by user id.
_history: dict[int, list] = {}
_MAX_HISTORY = 40

# Channels the bot answers in without being mentioned.
_AI_CHANNELS = ("ai-chat", "ai", "birdbrain")

_NO_KEY = "🤖 I have no Groq key configured. Ask an admin to set GROQ_API_KEY."


class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.key = bot.get_groq_key()

    # ── Core Groq call ────────────────────────────────────────
    async def _call(self, messages: list[dict]) -> str | None:
        if not self.key:
            return None
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(
                    GROQ_URL,
                    headers={"Authorization": f"Bearer {self.key}"},
                    json={"model": GROQ_MODEL, "messages": messages,
                          "max_tokens": 400, "temperature": 0.9},
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as r:
                    if r.status != 200:
                        print(f"Groq {r.status}: {(await r.text())[:200]}")
                        return None
                    data = await r.json()
            return data["choices"][0]["message"]["content"]
        except Exception as ex:
            print(f"Groq error: {ex}")
            return None

    async def chat(self, user_id: int, user_msg: str) -> str | None:
        """Continue a conversation with one user, keeping history."""
        hist = _history.setdefault(user_id, [])
        hist.append({"role": "user", "content": user_msg})
        if len(hist) > _MAX_HISTORY:
            hist[:] = hist[-_MAX_HISTORY:]
        reply = await self._call([{"role": "system", "content": SYSTEM_PROMPT}] + hist)
        if reply is None:
            return None
        hist.append({"role": "assistant", "content": reply})
        return reply

    async def _oneshot(self, instruction: str, user_msg: str) -> str | None:
        """Single call, no history kept."""
        return await self._call([
            {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + instruction},
            {"role": "user", "content": user_msg},
        ])

    async def roast(self, target: str) -> str | None:
        return await self._oneshot(
            "Your job right now: write ONE sharp roast of this person, 2 to 3 sentences. "
            "Dry, specific, funny rather than cruel. No preamble.",
            f"Roast this person. Display name: '{target}'.")

    async def topic(self) -> str | None:
        return await self._oneshot(
            "Your job right now: throw ONE spicy conversation starter or hot take, "
            "1 to 2 sentences. Make it worth arguing about.",
            "Give us a topic.")

    async def revive(self, guild_name: str) -> str | None:
        return await self._oneshot(
            f"Your job right now: one short line, 1 to 2 sentences, to wake up a dead chat "
            f"in {guild_name}. Be funny and a little mean.",
            "Chat is dead. Say something.")

    # ── Mention / #ai-chat listener ───────────────────────────
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        name = getattr(message.channel, "name", "") or ""
        if name.lower() not in _AI_CHANNELS:
            mentions_bot = bool(
                self.bot.user and message.mentions and self.bot.user in message.mentions)
            if not mentions_bot:
                return

        text = message.content.strip()
        # Ignore prefix commands, they are handled elsewhere.
        if text.startswith(("?", "!", ">", "/")):
            return
        # Strip the bot mention out of the text before sending it to Groq.
        if self.bot.user:
            text = text.replace(f"<@{self.bot.user.id}>", "").replace(
                f"<@!{self.bot.user.id}>", "").strip()
        if not text:
            return

        try:
            reply = await self.chat(message.author.id, text)
        except Exception as ex:
            print(f"AI respond error: {ex}")
            return
        if reply is None:
            return
        try:
            await message.channel.send(reply)
        except discord.Forbidden:
            pass

    # ── Commands ──────────────────────────────────────────────
    @app_commands.command(name="ask", description="Talk to the AI brain")
    async def slash_ask(self, i: discord.Interaction, *, message: str):
        rem = await check_cooldown(i.guild_id, i.user.id, "ask")
        if rem > 0:
            await i.response.send_message(f"⏳ Wait **{rem:.1f}s**.", ephemeral=True)
            return
        set_cooldown_ts(i.guild_id, i.user.id, "ask")
        await i.response.defer()
        reply = await self.chat(i.user.id, message)
        await i.followup.send(reply if reply else _NO_KEY,
                              ephemeral=reply is None)

    @app_commands.command(name="roast", description="Get roasted by the AI")
    async def slash_roast(self, i: discord.Interaction, target: discord.Member):
        rem = await check_cooldown(i.guild_id, i.user.id, "roast")
        if rem > 0:
            await i.response.send_message(f"⏳ Wait **{rem:.1f}s**.", ephemeral=True)
            return
        set_cooldown_ts(i.guild_id, i.user.id, "roast")
        await i.response.defer()
        reply = await self.roast(target.display_name)
        await i.followup.send(f"🔥 {reply}" if reply else _NO_KEY,
                              ephemeral=reply is None)

    @app_commands.command(name="topic", description="AI throws a conversation starter")
    async def slash_topic(self, i: discord.Interaction):
        await i.response.defer()
        reply = await self.topic()
        await i.followup.send(f"💬 {reply}" if reply else _NO_KEY,
                              ephemeral=reply is None)

    @app_commands.command(name="deadchat", description="AI tries to wake up dead chat")
    async def slash_deadchat(self, i: discord.Interaction):
        perm_role_id = await get_setting(i.guild.id, 'deadchat_perm_role')
        if perm_role_id:
            has = (any(r.id == perm_role_id for r in i.user.roles) or
                   i.user.guild_permissions.administrator)
            if not has:
                await i.response.send_message("❌ You can't use deadchat.", ephemeral=True)
                return
        await i.response.defer()
        guild_name = i.guild.name if i.guild else "this server"
        reply = await self.revive(guild_name)
        await i.followup.send(reply if reply else _NO_KEY,
                              ephemeral=reply is None,
                              allowed_mentions=discord.AllowedMentions.all())


async def setup(bot):
    await bot.add_cog(AI(bot))
