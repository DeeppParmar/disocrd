from bot.templates.base import (
    CategoryDefinition, ChannelDefinition, PermissionOverwriteDefinition,
    RoleDefinition, ServerTemplate, ServerType
)


class CreatorTemplate(ServerTemplate):
    """A content creator community server template."""
    
    @property
    def name(self) -> str:
        return "Content Creator"
    
    @property
    def description(self) -> str:
        return "Designed for YouTubers, Twitch streamers, and digital artists."
    
    @property
    def server_type(self) -> ServerType:
        return ServerType.CREATOR
    
    @property
    def roles(self) -> list[RoleDefinition]:
        return [
            RoleDefinition("owner", "🎬 Creator", "🎬", 0xFF0000, "OWNER", True, False, 100),
            RoleDefinition("manager", "📋 Manager", "📋", 0x3498DB, "ADMINISTRATOR", True, False, 90),
            RoleDefinition("moderator", "🔨 Mod", "🔨", 0x2ECC71, "MODERATOR", True, False, 80),
            RoleDefinition("vip", "⭐ Super Fan", "⭐", 0xF1C40F, "MEMBER", True, False, 70),
            RoleDefinition("subscriber", "📺 Subscriber", "📺", 0x9B59B6, "MEMBER", True, False, 60),
            RoleDefinition("member", "👋 Fan", "👋", 0x95A5A6, "MEMBER", False, False, 10),
            RoleDefinition("bots", "🤖 Bots", "🤖", 0x7289DA, "BOT", True, False, 15)
        ]
    
    @property
    def categories(self) -> list[CategoryDefinition]:
        return [
            CategoryDefinition("info", "📌 INFO", "📌", 0, [
                ChannelDefinition("announcements", "announcements", "announcement", "Creator announcements"),
                ChannelDefinition("rules", "rules", "text", "Community rules")
            ]),
            CategoryDefinition("content", "📺 CONTENT", "📺", 1, [
                ChannelDefinition("youtube", "youtube", "text", "New YouTube videos"),
                ChannelDefinition("twitch", "twitch", "text", "Twitch go-live notifications"),
                ChannelDefinition("tiktok", "tiktok", "text", "TikTok updates"),
                ChannelDefinition("instagram", "instagram", "text", "Instagram posts"),
                ChannelDefinition("showcase", "showcase", "text", "Community showcase")
            ]),
            CategoryDefinition("creative", "🎨 CREATIVE", "🎨", 2, [
                ChannelDefinition("art", "art", "text", "Fan art and creations"),
                ChannelDefinition("music", "music", "text", "Music sharing"),
                ChannelDefinition("writing", "writing", "text", "Stories and writing"),
                ChannelDefinition("photography", "photography", "text", "Photo sharing")
            ]),
            CategoryDefinition("business", "💼 BUSINESS", "💼", 3, [
                ChannelDefinition("collaborations", "collaborations", "text", "Collab requests"),
                ChannelDefinition("sponsorships", "sponsorships", "text", "Sponsorship talk")
            ]),
            CategoryDefinition("voice", "🎙️ VOICE", "🎙️", 4, [
                ChannelDefinition("podcast", "Podcast", "voice", user_limit=10),
                ChannelDefinition("recording", "Recording", "voice", user_limit=5),
                ChannelDefinition("watch_party", "Watch Party", "voice", user_limit=0)
            ])
        ]
    
    @property
    def permissions(self) -> dict[str, dict[str, PermissionOverwriteDefinition]]:
        return {
            "info": {
                "@everyone": PermissionOverwriteDefinition("@everyone", ["view_channel"], ["send_messages"])
            },
            "content": {
                "@everyone": PermissionOverwriteDefinition("@everyone", ["view_channel"], ["send_messages"]),
                "vip": PermissionOverwriteDefinition("vip", ["send_messages"], [])
            },
            "business": {
                "@everyone": PermissionOverwriteDefinition("@everyone", [], ["view_channel"]),
                "manager": PermissionOverwriteDefinition("manager", ["view_channel", "send_messages"], [])
            }
        }
    
    @property
    def automod_rules(self) -> list[dict]:
        return [
            {"name": "Block Profanity", "event_type": 1, "trigger_type": 4, "trigger_metadata": {"presets": [1, 2, 3]}, "actions": [{"type": 1}]}
        ]
    
    @property
    def features(self) -> dict[str, bool]:
        return {
            "COMMUNITY": True
        }
