# Discord API Limitations

> This document tracks all known Discord API limitations that affect this bot's functionality.
> Updated: 2026-09-14 | Discord API v10 | discord.py 2.7+

---

## Guild Management

| Limitation | Detail | Impact |
|------------|--------|--------|
| **Bots cannot create guilds for users** | Users must create servers manually and invite the bot | Bot workflow: User creates → invites bot → bot configures |
| **Server templates** | 1 template per guild; `POST /guilds/templates/{code}` limited to bots in <10 guilds | Template cloning uses bot's own snapshot system instead |
| **Community features** | Cannot be enabled by bots via API; requires manual activation in Discord UI | Bot detects Community status and adapts; prompts user to enable if needed |
| **Guild updates** | Some fields throttled to 2 requests per 10 seconds | Rate limit queue handles this |

## Channels & Categories

| Limitation | Detail |
|------------|--------|
| **Max channels** | 500 total per guild (all types including categories) |
| **Max categories** | 50 per guild |
| **Category capacity** | 50 channels per category |
| **Forum/Stage/Media channels** | Require `COMMUNITY` feature enabled on guild |
| **Channel name** | 1-100 characters, lowercase, no spaces (converted to hyphens) |
| **Channel topic** | Max 1024 characters (4096 for forum channels) |
| **Slowmode** | 0-21600 seconds (0-6 hours) |

## Roles

| Limitation | Detail |
|------------|--------|
| **Max roles** | 250 per guild (including `@everyone`) |
| **Role hierarchy** | Bot cannot manage roles at or above its highest role position |
| **Role name** | 1-100 characters |
| **Managed roles** | Bot/integration roles cannot be assigned/removed by the bot |

## Permissions

| Limitation | Detail |
|------------|--------|
| **Max overwrites** | 1000 unique permission overwrites per guild (error 30007/30013) |
| **Hierarchy enforcement** | Bot cannot grant permissions it doesn't have itself |
| **Administrator bypass** | Users with Administrator bypass all channel overwrites |

## Messages

| Limitation | Detail |
|------------|--------|
| **Bulk delete** | Max 100 messages per request; messages must be <14 days old |
| **Single delete** | Older messages can only be deleted individually (slower rate limit) |
| **Message content** | Requires `MESSAGE_CONTENT` privileged intent to read content in guild messages |
| **Embed limits** | Max 6000 characters total; max 25 fields; title max 256 chars |

## Interactions

| Limitation | Detail |
|------------|--------|
| **Response timeout** | 3 seconds to respond or defer; use `defer()` for longer operations |
| **Deferred timeout** | 15 minutes to send followup after deferring |
| **Components per message** | Max 5 Action Rows per message |
| **Buttons per row** | Max 5 buttons per Action Row |
| **Select menu** | Max 1 select menu per Action Row; max 25 options |
| **Modal text inputs** | Max 5 TextInput components per modal |
| **Custom ID** | Max 100 characters |

## AutoMod

| Limitation | Detail |
|------------|--------|
| **Total rules** | Max 10 rules per guild |
| **Keyword rules** | Max 6 |
| **Spam rule** | Max 1 |
| **Keyword preset** | Max 1 |
| **Mention spam** | Max 1 |
| **Member profile** | Max 1 |
| **Keywords per rule** | Max 1000 keywords; max 60 chars each |
| **Regex per rule** | Max 10 patterns; max 260 chars each |
| **Exempt roles** | Max 20 per rule |
| **Exempt channels** | Max 50 per rule |
| **Timeout duration** | Max 2,419,200 seconds (4 weeks) |

## Onboarding

| Limitation | Detail |
|------------|--------|
| **Requires Community** | Guild must have `COMMUNITY` feature enabled |
| **Default channels** | Minimum 7 default channels required |
| **Public channels** | At least 5 default channels must allow `@everyone` to view and send |
| **Permissions** | Requires `MANAGE_GUILD` and `MANAGE_ROLES` |

## Emoji & Stickers

| Boost Level | Static Emoji | Animated Emoji | Stickers |
|-------------|-------------|----------------|----------|
| Level 0 | 50 | 50 | 5 |
| Level 1 (2 boosts) | 100 | 100 | 15 |
| Level 2 (7 boosts) | 150 | 150 | 30 |
| Level 3 (14 boosts) | 250 | 250 | 60 |

## Rate Limits

| Scope | Limit |
|-------|-------|
| **Global** | 50 requests per second per bot token |
| **Invalid requests** | 10,000 per 10 minutes before IP ban |
| **Per-route** | Varies; tracked via `X-RateLimit-Bucket` header |
| **Webhook messages** | ~5 per second per webhook |
| **Channel messages** | ~5 per second per channel |
| **Guild updates** | ~2 per 10 seconds |

## Privileged Intents

| Intent | Required For | Verification Threshold |
|--------|-------------|----------------------|
| `GUILD_MEMBERS` | Member join/leave events, member chunking | 10,000 unique users |
| `MESSAGE_CONTENT` | Reading message content in guild messages | 10,000 unique users |
| `GUILD_PRESENCES` | Online/offline status, activities | 10,000 unique users |

- Below 100 guilds: can toggle freely in Developer Portal
- At 100 guilds: bot verification required (photo ID)
- At 10,000 users: privileged intent application required within 90-day grace period

## Other Limits

| Resource | Limit |
|----------|-------|
| **Audit logs** | 45-day retention |
| **Webhooks per channel** | 15 |
| **Bans list** | Paginated, no hard limit |
| **Scheduled events** | No hard limit documented |
| **Invite max age** | 0 (never) to 604800 seconds (7 days) |
| **Invite max uses** | 0 (unlimited) to 100 |
