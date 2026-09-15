from bot.templates.base import (
    CategoryDefinition, ChannelDefinition, PermissionOverwriteDefinition,
    RoleDefinition, ServerTemplate, ServerType
)


class CommunityTemplate(ServerTemplate):
    """A general community server template."""
    
    @property
    def name(self) -> str:
        return "Community Server"
    
    @property
    def description(self) -> str:
        return "A general-purpose community server with standard moderation, support, and engagement channels."
    
    @property
    def server_type(self) -> ServerType:
        return ServerType.COMMUNITY
    
    @property
    def roles(self) -> list[RoleDefinition]:
        return [
            RoleDefinition("owner", "👑 Server Owner", "👑", 0xFFD700, "OWNER", True, False, 100),
            RoleDefinition("head_admin", "🛡️ Head Administrator", "🛡️", 0xE74C3C, "ADMINISTRATOR", True, False, 90),
            RoleDefinition("admin", "🔧 Administrator", "🔧", 0xE67E22, "ADMINISTRATOR", True, False, 80),
            RoleDefinition("moderator", "🔨 Moderator", "🔨", 0x3498DB, "MODERATOR", True, False, 70),
            RoleDefinition("support", "🎫 Support", "🎫", 0x2ECC71, "SUPPORT", True, False, 60),
            RoleDefinition("helper", "🧰 Helper", "🧰", 0x1ABC9C, "HELPER", True, False, 50),
            RoleDefinition("vip", "⭐ VIP", "⭐", 0xF1C40F, "MEMBER", True, False, 40),
            RoleDefinition("premium", "💎 Premium", "💎", 0x9B59B6, "MEMBER", True, False, 35),
            RoleDefinition("verified", "✅ Verified", "✅", 0x2ECC71, "MEMBER", False, False, 20),
            RoleDefinition("member", "👤 Member", "👤", 0x95A5A6, "MEMBER", False, False, 10),
            RoleDefinition("muted", "🔇 Muted", "🔇", 0x7F8C8D, "MUTED", False, False, 5),
            RoleDefinition("quarantined", "⚠️ Quarantined", "⚠️", 0xE74C3C, "QUARANTINED", False, False, 1),
            RoleDefinition("bots", "🤖 Bots", "🤖", 0x7289DA, "BOT", True, False, 15)
        ]
    
    @property
    def categories(self) -> list[CategoryDefinition]:
        return [
            CategoryDefinition("information", "📌 INFORMATION", "📌", 0, [
                ChannelDefinition("rules", "rules", "text", "Please read and follow our server rules"),
                ChannelDefinition("announcements", "announcements", "announcement", "Official server announcements"),
                ChannelDefinition("welcome", "welcome", "text", "Welcome new members!"),
                ChannelDefinition("server_info", "server-info", "text", "Important server information"),
                ChannelDefinition("how_to_start", "how-to-start", "text", "Getting started guide"),
                ChannelDefinition("roles", "roles", "text", "Get your roles here")
            ]),
            CategoryDefinition("community", "💬 COMMUNITY", "💬", 1, [
                ChannelDefinition("general", "general", "text", "General discussion"),
                ChannelDefinition("chat", "chat", "text", "Casual conversation"),
                ChannelDefinition("media", "media", "text", "Share images, videos, and links"),
                ChannelDefinition("gaming", "gaming", "text", "Gaming discussion"),
                ChannelDefinition("memes", "memes", "text", "Share your memes"),
                ChannelDefinition("suggestions", "suggestions", "text", "Submit your suggestions")
            ]),
            CategoryDefinition("support", "🎫 SUPPORT", "🎫", 2, [
                ChannelDefinition("create_ticket", "create-ticket", "text", "Open a support ticket"),
                ChannelDefinition("ticket_archive", "ticket-archive", "text", "Archived tickets"),
                ChannelDefinition("applications", "applications", "text", "Apply for positions")
            ]),
            CategoryDefinition("staff", "🛡️ STAFF", "🛡️", 3, [
                ChannelDefinition("staff_chat", "staff-chat", "text", "Staff discussion"),
                ChannelDefinition("mod_chat", "mod-chat", "text", "Moderator discussion"),
                ChannelDefinition("reports", "reports", "text", "Member reports"),
                ChannelDefinition("mod_logs", "mod-logs", "text", "Moderation action logs"),
                ChannelDefinition("server_logs", "server-logs", "text", "Server event logs"),
                ChannelDefinition("staff_room", "Staff Room", "voice")
            ]),
            CategoryDefinition("voice", "🔊 VOICE", "🔊", 4, [
                ChannelDefinition("voice_general", "General", "voice", user_limit=0),
                ChannelDefinition("voice_gaming", "Gaming", "voice", user_limit=10),
                ChannelDefinition("voice_music", "Music", "voice", user_limit=5),
                ChannelDefinition("voice_afk", "AFK", "voice", user_limit=0),
                ChannelDefinition("voice_create", "➕ Create Room", "voice", user_limit=1)
            ])
        ]
    
    @property
    def permissions(self) -> dict[str, dict[str, PermissionOverwriteDefinition]]:
        return {
            "information": {
                "@everyone": PermissionOverwriteDefinition("@everyone", ["view_channel", "read_message_history"], ["send_messages", "add_reactions"])
            },
            "welcome": {
                "@everyone": PermissionOverwriteDefinition("@everyone", ["view_channel", "read_message_history"], ["send_messages"])
            },
            "staff": {
                "@everyone": PermissionOverwriteDefinition("@everyone", [], ["view_channel"]),
                "moderator": PermissionOverwriteDefinition("moderator", ["view_channel", "send_messages", "read_message_history"], [])
            },
            "create_ticket": {
                "@everyone": PermissionOverwriteDefinition("@everyone", ["view_channel", "read_message_history"], ["send_messages"]),
                "staff": PermissionOverwriteDefinition("moderator", ["view_channel", "send_messages", "manage_messages"], [])
            },
            "staff_room": {
                "@everyone": PermissionOverwriteDefinition("@everyone", [], ["view_channel", "connect"]),
                "moderator": PermissionOverwriteDefinition("moderator", ["view_channel", "connect", "speak"], [])
            }
        }
    
    @property
    def automod_rules(self) -> list[dict]:
        return [
            {"name": "Block Profanity", "event_type": 1, "trigger_type": 4, "trigger_metadata": {"presets": [1, 2, 3]}, "actions": [{"type": 1}]},
            {"name": "Block Spam", "event_type": 1, "trigger_type": 3, "actions": [{"type": 1}]},
            {"name": "Block Mention Spam", "event_type": 1, "trigger_type": 5, "trigger_metadata": {"mention_total_limit": 5}, "actions": [{"type": 1}]}
        ]
    
    @property
    def features(self) -> dict[str, bool]:
        return {
            "COMMUNITY": True,
            "WELCOME_SCREEN_ENABLED": True,
            "INVITE_SPLASH": True,
            "DISCOVERABLE": False
        }
