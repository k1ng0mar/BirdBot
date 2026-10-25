# That One Bird manual

This is the reference for everything the bot does. Every command works two ways: as a slash
command (`/name`) and with the prefix (`?name`). The prefix is `?` by default and can be
changed per server with the prefix command in Server configuration.

Use `/manual <topic>` to pull up one section, or just ask the bot in chat. The AI reads this
file to answer "how do I..." questions, and it also reads the live server settings when the
question is about this specific server.

<!-- kw: manual, docs, documentation, help, guide, readme, commands, list, everything -->

## How commands work

<!-- kw: how do commands work, slash vs prefix, command syntax, do i need a prefix -->

Every command registers twice, once as `/name` and once as `?name`. Both do the same thing.
Slash commands give you autocomplete and pickers. Prefix commands let you type faster.

### Replying to target

Reply to someone's message when you run a moderation command and the bot targets that person
instead of requiring you to type their name. It also attaches their message as proof in the mod
log, with a jump link. This works on the prefix versions of the moderation commands.

<!-- kw: reply, target, proof, mention, attach, jump link, modlog -->

### Command display modes

A command response can be public (everyone sees it), ephemeral (only the person who ran it
sees it), or timed (posted then deleted after N seconds). Set it from Server configuration. Default
is public.

<!-- kw: display, ephemeral, public, timed, hidden, invisible, delete response -->

### Cooldowns

Some commands have per-user rate limits so they cannot be spammed. Defaults: deadchat 3600s,
meme 10s, roast 15s, 8ball 5s, poll 30s, urban 10s. Everything else defaults to 30s. Override
any of them from Server configuration.

<!-- kw: cooldown, spam, rate limit, wait, seconds, override -->

## Moderation commands

All moderation commands need the matching Discord permission. Mute, jail, nick, and warn need
Moderate Members. Kick needs Kick Members. Ban needs Ban Members. Purge needs Manage Messages.
Slowmode needs Manage Channels. `/setup` and every `/set*` command need Administrator.

<!-- kw: moderation, mod, admin, punish, permission, who can, role -->

| Command | What it does |
| --- | --- |
| `/warn @user <reason>` | Adds a warn. Shows the running count. Optional `expires_in` sets when it lapses. |
| `/unwarn @user <warn_id>` | Removes one warn by its ID. |
| `/clearwarns @user` | Wipes every warn for a user. |
| `/warns @user` | Lists active warns for a user. |
| `/history @user` | Every mod action ever taken against a user, from the mod log. |
| `/modlogs @mod` | Every action a moderator has taken. |
| `/mute @user <minutes> <reason>` | Timeout. DMs the user when it ends. `0` clears it early. |
| `/unmute @user` | Removes a timeout. |
| `/kick @user <reason>` | Kicks. |
| `/ban @user <reason>` | Bans. |
| `/tempban @user <duration> <reason>` | Bans, then unbans automatically. |
| `/unban <user_id>` | Unbans by ID. Works on users who are not in the server. |
| `/jail @user <reason>` | Takes their roles, gives the jail role, sends them to the jail channel. |
| `/unjail @user` | Gives their roles back. |
| `/purge <amount>` | Bulk delete. Max 100 at a time. |
| `/nick @user <nickname>` | Changes a nickname. |
| `/slowmode <seconds>` | Sets channel slowmode. `0` turns it off. |
| `/lookup <user_id>` | Fetches info about any user by ID, even one not in the server. |

<!-- kw: warn, unwarn, clearwarns, warns, history, modlogs, mute, unmute, kick, ban, tempban, unban, jail, unjail, purge, nick, slowmode, lookup, moderation, timeout -->

### Durations

Durations are `<number><unit>` with unit `d`, `h`, or `m`. `7d`, `24h`, `30m`, `1d`. This format
is used by tempban, mute, reminders, automod warn expiry, and the warn threshold mute length.

<!-- kw: duration, time, format, days, hours, minutes, 7d, 24h, 30m, tempban -->

## Warn system and thresholds

Warns stack. When someone hits a set number of warns the bot acts on its own.

- `/setwarnthreshold kick 3` kicks at 3 warns.
- `/setwarnthreshold ban 5` bans at 5.
- `/setwarnthreshold mute 4 10` mutes for 10 minutes at 4 warns.
- Count `0` disables that action.

Warns can expire. Set the default expiry for automod warns with `/automod setwarnexpiry 7d`.
Manual warns stay until removed or cleared.

Check the current thresholds with `/setup`.

<!-- kw: warn, threshold, escalate, auto kick, auto ban, auto mute, count, expire, escalate -->

## Automod

A word filter. When a message contains a filtered word the bot deletes it, then acts based on
the configured action.

Actions:

- `delete_only`: deletes the message, posts a short notice.
- `warn`: deletes, adds a warn, logs it, DMs the user their warn count.
- `mute`: deletes, times the user out, logs it, DMs them.

Matching uses word boundaries, so filtering `ass` does not flag `class` or `grass`.

Commands:

- `/automod toggle` turns it on or off.
- `/automod addword <word>` adds to the filter.
- `/automod removeword <word>` removes one.
- `/automod listwords` shows the whole filter.
- `/automod setaction <delete_only|warn|mute>` sets what happens.
- `/automod setmuteduration <minutes>` sets the mute length.
- `/automod setwarnexpiry <duration>` sets when automod warns lapse, for example `7d`.

Automod is on by default with `delete_only`.

<!-- kw: automod, filter, bad word, profanity, word filter, delete, warn, mute, blocked, banned word -->

## Anti-raid

<!-- kw: antiraid, anti-raid, raid, lockdown, slowmode, mass join, burst, kick new -->

Watches for a burst of joins. If too many people join inside the window, the bot acts.

- `slowmode`: 60 second slowmode on the raid channel.
- `lockdown`: locks the channel.
- `kick_new`: kicks the new joins.

Commands:

- `/antiraidtoggle` turns it on or off.
- `/antiraidsettings <threshold> <seconds> <action>` sets it. Example: `5 10 kick_new`.

It is off by default.

## Roles

<!-- kw: role, roles, add role, remove role, create role, delete role, color, roleinfo, roleadd, roleremove, rolelist, make a role, make role, give role, new role, delete a role, give someone a role, add a role, role commands -->

| Command | What it does |
| --- | --- |
| `/add @user @role` | Gives a role. |
| `/remove @user @role` | Takes a role. |
| `/info @role` | Role details. |
| `/list` | Every role in the server. |
| `/create <name> [color]` | Makes a role. |
| `/delete @role` | Deletes a role. |
| `/color @role <color>` | Changes a role color. |

All role commands need Manage Roles. Prefix shortcuts exist: `?roleadd`, `?roleremove`,
`?roleinfo`, `?rolelist`.

<!-- kw: role, roles, add role, remove role, create role, delete role, color, roleinfo -->

## Server configuration

Run `/setup` to see every current setting in one panel. It shows the prefix, all four log
channels, welcome, autorole, jail, starboard, automod, anti-raid, and warn thresholds.

Change any of them with the matching `/set*` command. All of these need Administrator.

<!-- kw: setup, settings, configure, config, set, admin panel, dashboard, whats the prefix, change prefix, set prefix, prefix, setlogchannel, setwelcome, setautorole, setjail, setstarboard, setcooldown, setdisplay, setcommandperms, antiraidsettings, setwarnthreshold -->

| Command | What it does |
| --- | --- |
| `/setprefix <prefix>` | Changes the prefix for this server. |
| `/setlogchannel <mod\|messages\|members\|server> #channel` | Routes one log category to a channel. |
| `/setwelcome #channel <message>` | Sets the welcome channel and message. |
| `/setautorole @role` | Gives this role to everyone who joins. |
| `/setjail #channel @role` | Sets the jail channel and jail role. |
| `/setdeadchatrole @role` | Role pinged by `/deadchat`. |
| `/setdeadchatperm @role` | Restricts `/deadchat` to this role. Leave empty to open it up. |
| `/setstarboard #channel <emoji> <threshold>` | Configures the starboard. |
| `/setcooldown <command> <seconds>` | Overrides a cooldown. |
| `/setcommandperms <command> @role [silent]` | Restricts a command to a role. |
| `/setdisplay <command> <mode> [seconds]` | Sets how a response appears. |
| `/antiraidsettings` | Configures anti-raid. |
| `/antiraidtoggle` | Enables or disables anti-raid. |
| `/setwarnthreshold` | Sets an action at a warn count. |

### Welcome message placeholders

The welcome message supports four placeholders: `{user}` mentions the new member, `{name}` is
their display name, `{server}` is the server name, `{count}` is the member count.

<!-- kw: welcome, placeholders, user, name, server, count, autorole -->

## Logging

Four separate log channels, each set independently with `/setlogchannel`. Logs go to whichever
you set and nowhere else. If one is not set, that category is silent.

- `mod`: moderation actions. Warn, mute, kick, ban, jail, purge, automod, everything.
- `messages`: message deletes and edits.
- `members`: joins, leaves, role changes, nick changes.
- `server`: channel create and delete, invite create, voice state changes.

The bot also syncs the Discord audit log, so bans and kicks done by hand outside the bot still
appear in `/history` and `/modlogs`.

<!-- kw: logs, logging, log, channels, audit, modlogs, mod log, message log, member log, server log, log channels -->

## Jail

Jail is a real isolation, not a ban. Running `/jail @user`:

1. Takes every role they have.
2. Stores those roles in the database.
3. Gives them the jail role you set with `/setjail`.
4. Posts in the jail channel.

`/unjail @user` restores the stored roles and removes the jail role. If the roles are deleted
while they are jailed, only the ones that still exist come back.

You need both a jail channel and a jail role configured or jail does nothing. `/setup` shows
whether they are set.

<!-- kw: jail, isolate, prison, lockdown, unjail, jailed role -->

## Starboard

Messages that collect the configured emoji up to the threshold get reposted to the starboard
channel. Set it with `/setstarboard #channel ⭐ 3`. Change the emoji and threshold freely. The
bot tracks which messages it already posted so it does not double post.

<!-- kw: starboard, star, highlight, emoji, threshold, repost -->

## Deadchat

`/deadchat` posts a random line to wake the server up. It has a 3600 second per-user cooldown by
default. If you set a deadchat role with `/setdeadchatrole`, it pings that role. If you set a
permission role with `/setdeadchatperm`, only people with that role (or admins) can use it.

<!-- kw: deadchat, dead chat, wake up, revive, ping, revive server -->

## Triggers

Auto replies. Add a word or phrase and what the bot should say when it shows up.

- `/settrigger <trigger> <response> <contains|startswith>` adds one.
- `/listtriggers` shows them all.
- `/deletetrigger <trigger_id>` removes one by its ID.

`contains` fires when the trigger appears anywhere in a message. `startswith` fires when the
message begins with it.

<!-- kw: trigger, auto reply, keyword, response, contains, startswith, autoreply -->

## Custom commands

Build your own commands with `/addcommand <name> <type> <value>`. Three types:

- `message`: posts the value as text.
- `ping`: mentions a role or user with the value as the target.
- `alias`: runs another command. Put the target command in the value.

`/listcommands` shows them. `/deletecommand <name>` removes one.

Custom commands respect the same cooldown, permission, and display settings as built-in ones.

<!-- kw: custom command, addcommand, alias, own command, create command, deletecommand -->

## The AI brain

The bot has a Groq powered brain. Talk to it two ways: mention it anywhere, or post in a channel
named `ai-chat`, `ai`, or `birdbrain` and it answers without being mentioned.

Commands:

- `/ask <message>` asks it something directly.
- `/roast @user` gets a roast aimed at that person.
- `/topic` throws a conversation starter.
- `/deadchat` tries to wake the server up.

It is a roast comic with a bad attitude. It swears, it does not soften for a general audience,
and it is not a helpful assistant. It reads the room though. If someone is having a rough time it
drops the act.

The brain needs `GROQ_API_KEY` in `.env`. Without it, the AI commands do nothing.

<!-- kw: ai, brain, groq, ask, roast, chat, mention, ai-chat, llama, qwen, model -->

## Fun and utilities

| Command | What it does |
| --- | --- |
| `/meme` | Random meme. |
| `/8ball <question>` | Magic 8-ball. |
| `/poll <question> <2 to 4 options>` | Creates a poll. |
| `/remind <time> <message>` | Reminds you. `30m`, `2h`, `1d`. |
| `/snipe` | Last deleted messages. |
| `/esnipe` | Recently edited messages, with before and after. |
| `/afk [reason]` | Marks you AFK. Clears when you talk again. Pings people who mention you. |
| `/say <message> [role]` | Makes the bot say something. |
| `/announce <channel> <message> [role]` | Posts to any channel. |
| `/pingrole @role` | Pings a role. |
| `/hug`, `/slap`, `/bite`, `/punch`, `/kick` | Aimed at a member, playful. |
| `/avatar [@user]` | Someone's avatar. |
| `/banner [@user]` | Someone's profile banner. |
| `/servericon` | The server icon. |
| `/quote` | Quote image from the message you reply to. Prefix only. |
| `/coinflip` | Flip a coin. |
| `/dice [sides]` | Roll. Defaults to 6 sides. |
| `/calc <expression>` | Math. |
| `/urban <term>` | Urban Dictionary lookup. |
| `/firstmessage [@user]` | Link to their first message in the channel. |
| `/steal <emoji> [name]` | Steals an emoji from another server. |
| `/mybookmarks` | Your bookmarks. React 🔖 to any message to save it. |

<!-- kw: fun, meme, 8ball, poll, remind, snipe, esnipe, afk, say, announce, pingrole, hug, slap, bite, punch, kick, avatar, banner, servericon, quote, coinflip, dice, calc, urban, firstmessage, steal, bookmark -->

## Animal pictures

Ten animal picture commands: `/cat` `/dog` `/fox` `/duck` `/panda` `/bunny` `/koala` `/bird`
`/hamster` `/raccoon`.

<!-- kw: animal, cat, dog, fox, duck, panda, bunny, koala, bird, hamster, raccoon, pic, picture -->

## Server info

- `/userinfo [@user]` for member details.
- `/serverinfo` for the server.
- `/ping` for bot latency.
- `/help` for the command list.
- `/manual <topic>` for anything in this file.

<!-- kw: userinfo, serverinfo, ping, help, manual, info, latency -->

## Who can do what

Three layers, checked in this order:

1. Discord permissions. Moderation commands check the matching permission. Config commands need
   Administrator.
2. Per-command role restriction. `/setcommandperms` can lock a command to a role. Admins always
   pass. With `silent` on, unauthorized uses are ignored instead of rejected.
3. Cooldowns. The last gate, per user per command.

Automod, anti-raid, triggers, and custom commands run on their own and do not check any of this.

<!-- kw: permission, who can, access, restrict, lock command, role restriction, allowed -->

## Troubleshooting

**A command does nothing.** Check `/setup` for the setting it needs. Jail needs a channel and a
role. Starboard needs a channel. Deadchat pings nothing if no role is set. The AI needs a key.

**A log is empty.** That log channel is probably not set. Run `/setlogchannel` for the category.

**The bot ignores messages.** Check that Message Content Intent is enabled in the Discord
developer portal, under the bot's settings. Without it the bot cannot read message text, so
automod, triggers, and AI chat silently do nothing.

**The bot has no permissions.** Check its role position in server settings. A role higher than
the bot's own role cannot be managed by it, and it cannot moderate anyone with a higher role.

**The prefix changed.** `/setprefix` is per server. Check `/setup`.

<!-- kw: troubleshooting, problem, broken, not working, fix, empty, no permissions, intent, message content intent, nothing happens -->
