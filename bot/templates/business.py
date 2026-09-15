from bot.templates.base import (
    CategoryDefinition, ChannelDefinition, PermissionOverwriteDefinition,
    RoleDefinition, ServerTemplate, ServerType
)


class BusinessTemplate(ServerTemplate):
    """A business and professional networking server template."""
    
    @property
    def name(self) -> str:
        return "Business & Networking"
    
    @property
    def description(self) -> str:
        return "For companies, agencies, and professional groups."
    
    @property
    def server_type(self) -> ServerType:
        return ServerType.BUSINESS
    
    @property
    def roles(self) -> list[RoleDefinition]:
        return [
            RoleDefinition("ceo", "👔 CEO/Founder", "👔", 0x34495E, "OWNER", True, False, 100),
            RoleDefinition("director", "📊 Director", "📊", 0x9B59B6, "ADMINISTRATOR", True, False, 90),
            RoleDefinition("manager", "📋 Manager", "📋", 0x2980B9, "MODERATOR", True, False, 80),
            RoleDefinition("employee", "💼 Employee", "💼", 0x2ECC71, "MEMBER", True, False, 50),
            RoleDefinition("contractor", "🤝 Contractor", "🤝", 0xE67E22, "MEMBER", True, False, 40),
            RoleDefinition("client", "⭐ Client", "⭐", 0xF1C40F, "MEMBER", True, False, 30),
            RoleDefinition("guest", "👤 Guest", "👤", 0x95A5A6, "MEMBER", False, False, 10),
            RoleDefinition("bots", "🤖 Bots", "🤖", 0x7289DA, "BOT", True, False, 15)
        ]
    
    @property
    def categories(self) -> list[CategoryDefinition]:
        return [
            CategoryDefinition("general", "📋 GENERAL", "📋", 0, [
                ChannelDefinition("announcements", "announcements", "announcement", "Company announcements"),
                ChannelDefinition("general_chat", "general", "text", "General discussion"),
                ChannelDefinition("introductions", "introductions", "text", "Introduce yourself")
            ]),
            CategoryDefinition("departments", "💼 DEPARTMENTS", "💼", 1, [
                ChannelDefinition("marketing", "marketing", "text", "Marketing team"),
                ChannelDefinition("engineering", "engineering", "text", "Engineering team"),
                ChannelDefinition("sales", "sales", "text", "Sales team"),
                ChannelDefinition("hr", "hr", "text", "Human Resources")
            ]),
            CategoryDefinition("projects", "📊 PROJECTS", "📊", 2, [
                ChannelDefinition("active_projects", "active-projects", "text", "Current initiatives"),
                ChannelDefinition("completed", "completed", "text", "Finished work"),
                ChannelDefinition("resources", "resources", "text", "Assets and links")
            ]),
            CategoryDefinition("networking", "🤝 NETWORKING", "🤝", 3, [
                ChannelDefinition("opportunities", "opportunities", "text", "Job postings and gigs"),
                ChannelDefinition("events", "events", "text", "Upcoming events")
            ]),
            CategoryDefinition("voice", "🎙️ VOICE", "🎙️", 4, [
                ChannelDefinition("meeting_room_1", "Meeting Room 1", "voice", user_limit=10),
                ChannelDefinition("meeting_room_2", "Meeting Room 2", "voice", user_limit=10),
                ChannelDefinition("presentation", "Presentation", "voice", user_limit=0)
            ])
        ]
    
    @property
    def permissions(self) -> dict[str, dict[str, PermissionOverwriteDefinition]]:
        return {
            "departments": {
                "@everyone": PermissionOverwriteDefinition("@everyone", [], ["view_channel"]),
                "employee": PermissionOverwriteDefinition("employee", ["view_channel", "send_messages"], [])
            }
        }
    
    @property
    def automod_rules(self) -> list[dict]:
        return []
    
    @property
    def features(self) -> dict[str, bool]:
        return {
            "COMMUNITY": True
        }
