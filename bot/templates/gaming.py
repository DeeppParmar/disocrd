from bot.templates.base import (
    CategoryDefinition, ChannelDefinition, PermissionOverwriteDefinition,
    RoleDefinition, ServerTemplate, ServerType
)


class GamingTemplate(ServerTemplate):
    """A gaming-focused server template."""
    
    @property
    def name(self) -> str:
        return "Gaming Community"
    
    @property
    def description(self) -> str:
        return "Perfect for gaming groups, clans, and esports teams."
    
    @property
    def server_type(self) -> ServerType:
        return ServerType.GAMING
    
    @property
    def roles(self) -> list[RoleDefinition]:
        return [
            RoleDefinition("owner", "👑 Guild Leader", "👑", 0xFFD700, "OWNER", True, False, 100),
            RoleDefinition("admin", "🛡️ Warlord", "🛡️", 0xE74C3C, "ADMINISTRATOR", True, False, 90),
            RoleDefinition("moderator", "🔨 Sentinel", "🔨", 0x3498DB, "MODERATOR", True, False, 80),
            RoleDefinition("competitive", "🏆 Competitive", "🏆", 0xE67E22, "MEMBER", True, False, 70),
            RoleDefinition("streamer", "📺 Streamer", "📺", 0x9B59B6, "MEMBER", True, False, 60),
            RoleDefinition("veteran", "⭐ Veteran", "⭐", 0xF1C40F, "MEMBER", True, False, 50),
            RoleDefinition("member", "🎮 Player", "🎮", 0x2ECC71, "MEMBER", False, False, 10),
            RoleDefinition("muted", "🔇 Muted", "🔇", 0x7F8C8D, "MUTED", False, False, 5),
            RoleDefinition("bots", "🤖 Bots", "🤖", 0x7289DA, "BOT", True, False, 15)
        ]
    
    @property
    def categories(self) -> list[CategoryDefinition]:
        return [
            CategoryDefinition("information", "📌 INFORMATION", "📌", 0, [
                ChannelDefinition("rules", "rules", "text", "Server rules"),
                ChannelDefinition("announcements", "announcements", "announcement", "Server announcements")
            ]),
            CategoryDefinition("general", "💬 GENERAL", "💬", 1, [
                ChannelDefinition("chat", "chat", "text", "General chat"),
                ChannelDefinition("media", "media", "text", "Share media"),
                ChannelDefinition("memes", "memes", "text", "Memes")
            ]),
            CategoryDefinition("games", "🎮 GAMES", "🎮", 2, [
                ChannelDefinition("minecraft", "minecraft", "text", "Minecraft discussion"),
                ChannelDefinition("valorant", "valorant", "text", "Valorant discussion"),
                ChannelDefinition("gta", "gta", "text", "GTA discussion"),
                ChannelDefinition("fortnite", "fortnite", "text", "Fortnite discussion"),
                ChannelDefinition("other_games", "other-games", "text", "Other games")
            ]),
            CategoryDefinition("competitive", "🏆 COMPETITIVE", "🏆", 3, [
                ChannelDefinition("lfg", "lfg", "text", "Looking for group"),
                ChannelDefinition("tournaments", "tournaments", "text", "Tournament info"),
                ChannelDefinition("rankings", "rankings", "text", "Leaderboards")
            ]),
            CategoryDefinition("streaming", "📺 STREAMING", "📺", 4, [
                ChannelDefinition("clips", "clips", "text", "Epic clips"),
                ChannelDefinition("streams", "streams", "text", "Live streams"),
                ChannelDefinition("highlights", "highlights", "text", "Stream highlights")
            ]),
            CategoryDefinition("voice", "🔊 VOICE", "🔊", 5, [
                ChannelDefinition("voice_gamenight", "Game Night", "voice", user_limit=0),
                ChannelDefinition("voice_competitive", "Competitive", "voice", user_limit=5),
                ChannelDefinition("voice_casual", "Casual", "voice", user_limit=0),
                ChannelDefinition("voice_streaming", "Streaming", "voice", user_limit=0)
            ])
        ]
    
    @property
    def permissions(self) -> dict[str, dict[str, PermissionOverwriteDefinition]]:
        return {
            "information": {
                "@everyone": PermissionOverwriteDefinition("@everyone", ["view_channel", "read_message_history"], ["send_messages"])
            },
            "competitive": {
                "@everyone": PermissionOverwriteDefinition("@everyone", ["view_channel"], ["send_messages"]),
                "competitive": PermissionOverwriteDefinition("competitive", ["send_messages"], [])
            }
        }
    
    @property
    def automod_rules(self) -> list[dict]:
        return [
            {"name": "Block Profanity", "event_type": 1, "trigger_type": 4, "trigger_metadata": {"presets": [1, 2, 3]}, "actions": [{"type": 1}]},
            {"name": "Block Spam", "event_type": 1, "trigger_type": 3, "actions": [{"type": 1}]}
        ]
    
    @property
    def features(self) -> dict[str, bool]:
        return {
            "COMMUNITY": True
        }
