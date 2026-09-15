from bot.templates.base import (
    CategoryDefinition, ChannelDefinition, PermissionOverwriteDefinition,
    RoleDefinition, ServerTemplate, ServerType
)


class FriendsTemplate(ServerTemplate):
    """A minimal server template for friend groups."""
    
    @property
    def name(self) -> str:
        return "Friends & Chill"
    
    @property
    def description(self) -> str:
        return "A simple, relaxed server for small groups of friends."
    
    @property
    def server_type(self) -> ServerType:
        return ServerType.FRIENDS
    
    @property
    def roles(self) -> list[RoleDefinition]:
        return [
            RoleDefinition("owner", "👑 Owner", "👑", 0xFFD700, "OWNER", True, False, 100),
            RoleDefinition("admin", "🛡️ Admin", "🛡️", 0xE74C3C, "ADMINISTRATOR", True, False, 90),
            RoleDefinition("member", "👤 Friend", "👤", 0x2ECC71, "MEMBER", False, False, 10),
            RoleDefinition("bots", "🤖 Bots", "🤖", 0x7289DA, "BOT", True, False, 15)
        ]
    
    @property
    def categories(self) -> list[CategoryDefinition]:
        return [
            CategoryDefinition("hangout", "💬 HANGOUT", "💬", 0, [
                ChannelDefinition("general", "general", "text", "General chat"),
                ChannelDefinition("memes", "memes", "text", "Funny stuff"),
                ChannelDefinition("music", "music", "text", "Music recommendations"),
                ChannelDefinition("gaming", "gaming", "text", "Game chat"),
                ChannelDefinition("photos", "photos", "text", "IRL pics and photos")
            ]),
            CategoryDefinition("voice", "🔊 VOICE", "🔊", 1, [
                ChannelDefinition("hangout_vc", "Hangout", "voice", user_limit=0),
                ChannelDefinition("gaming_vc", "Gaming", "voice", user_limit=0),
                ChannelDefinition("music_vc", "Music", "voice", user_limit=0),
                ChannelDefinition("afk_vc", "AFK", "voice", user_limit=0)
            ])
        ]
    
    @property
    def permissions(self) -> dict[str, dict[str, PermissionOverwriteDefinition]]:
        return {}
    
    @property
    def automod_rules(self) -> list[dict]:
        return []
    
    @property
    def features(self) -> dict[str, bool]:
        return {
            "COMMUNITY": False
        }
