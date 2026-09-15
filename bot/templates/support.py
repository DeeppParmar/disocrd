from bot.templates.base import (
    CategoryDefinition, ChannelDefinition, PermissionOverwriteDefinition,
    RoleDefinition, ServerTemplate, ServerType
)


class SupportTemplate(ServerTemplate):
    """A technical or product support server template."""
    
    @property
    def name(self) -> str:
        return "Product Support"
    
    @property
    def description(self) -> str:
        return "Ideal for software, hardware, or service support communities."
    
    @property
    def server_type(self) -> ServerType:
        return ServerType.SUPPORT
    
    @property
    def roles(self) -> list[RoleDefinition]:
        return [
            RoleDefinition("owner", "🏢 Founder", "🏢", 0x34495E, "OWNER", True, False, 100),
            RoleDefinition("manager", "📈 Product Manager", "📈", 0x9B59B6, "ADMINISTRATOR", True, False, 90),
            RoleDefinition("support_lead", "👨‍💻 Support Lead", "👨‍💻", 0xE74C3C, "MODERATOR", True, False, 80),
            RoleDefinition("tech_support", "🔧 Tech Support", "🔧", 0xE67E22, "SUPPORT", True, False, 70),
            RoleDefinition("billing_support", "💳 Billing Support", "💳", 0x2ECC71, "SUPPORT", True, False, 60),
            RoleDefinition("customer", "👤 Customer", "👤", 0x3498DB, "MEMBER", False, False, 10),
            RoleDefinition("bots", "🤖 Bots", "🤖", 0x7289DA, "BOT", True, False, 15)
        ]
    
    @property
    def categories(self) -> list[CategoryDefinition]:
        return [
            CategoryDefinition("knowledge_base", "📖 KNOWLEDGE BASE", "📖", 0, [
                ChannelDefinition("docs", "docs", "text", "Documentation links"),
                ChannelDefinition("faq", "faq", "text", "Frequently Asked Questions"),
                ChannelDefinition("guides", "guides", "text", "Step-by-step guides"),
                ChannelDefinition("tutorials", "tutorials", "text", "Video and text tutorials")
            ]),
            CategoryDefinition("support", "🎫 SUPPORT", "🎫", 1, [
                ChannelDefinition("general_support", "general-support", "text", "General queries"),
                ChannelDefinition("billing", "billing", "text", "Billing and payments"),
                ChannelDefinition("technical", "technical", "text", "Technical help"),
                ChannelDefinition("bug_reports", "bug-reports", "forum", "Report issues")
            ]),
            CategoryDefinition("updates", "📢 UPDATES", "📢", 2, [
                ChannelDefinition("changelog", "changelog", "announcement", "Product updates"),
                ChannelDefinition("roadmap", "roadmap", "text", "Future plans"),
                ChannelDefinition("status", "status", "text", "System status")
            ])
        ]
    
    @property
    def permissions(self) -> dict[str, dict[str, PermissionOverwriteDefinition]]:
        return {
            "knowledge_base": {
                "@everyone": PermissionOverwriteDefinition("@everyone", ["view_channel"], ["send_messages"])
            },
            "updates": {
                "@everyone": PermissionOverwriteDefinition("@everyone", ["view_channel"], ["send_messages"])
            }
        }
    
    @property
    def automod_rules(self) -> list[dict]:
        return [
            {"name": "Block Spam", "event_type": 1, "trigger_type": 3, "actions": [{"type": 1}]}
        ]
    
    @property
    def features(self) -> dict[str, bool]:
        return {
            "COMMUNITY": True
        }
