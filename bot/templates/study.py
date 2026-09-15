from bot.templates.base import (
    CategoryDefinition, ChannelDefinition, PermissionOverwriteDefinition,
    RoleDefinition, ServerTemplate, ServerType
)


class StudyTemplate(ServerTemplate):
    """An educational or study group server template."""
    
    @property
    def name(self) -> str:
        return "Study Group"
    
    @property
    def description(self) -> str:
        return "For study groups, classes, or academic clubs."
    
    @property
    def server_type(self) -> ServerType:
        return ServerType.STUDY
    
    @property
    def roles(self) -> list[RoleDefinition]:
        return [
            RoleDefinition("owner", "🎓 Professor / Leader", "🎓", 0x8E44AD, "OWNER", True, False, 100),
            RoleDefinition("admin", "📚 TA / Admin", "📚", 0x2980B9, "ADMINISTRATOR", True, False, 90),
            RoleDefinition("tutor", "💡 Tutor", "💡", 0x27AE60, "MODERATOR", True, False, 80),
            RoleDefinition("student", "📝 Student", "📝", 0x3498DB, "MEMBER", False, False, 10),
            RoleDefinition("bots", "🤖 Bots", "🤖", 0x7289DA, "BOT", True, False, 15)
        ]
    
    @property
    def categories(self) -> list[CategoryDefinition]:
        return [
            CategoryDefinition("academics", "📚 ACADEMICS", "📚", 0, [
                ChannelDefinition("study_chat", "study-chat", "text", "General academic chat"),
                ChannelDefinition("homework_help", "homework-help", "text", "Get help with assignments"),
                ChannelDefinition("resources", "resources", "text", "Useful links and files"),
                ChannelDefinition("notes", "notes", "text", "Share notes")
            ]),
            CategoryDefinition("subjects", "🔬 SUBJECTS", "🔬", 1, [
                ChannelDefinition("math", "math", "text", "Mathematics"),
                ChannelDefinition("science", "science", "text", "Sciences"),
                ChannelDefinition("english", "english", "text", "English / Literature"),
                ChannelDefinition("history", "history", "text", "History"),
                ChannelDefinition("programming", "programming", "text", "Computer Science")
            ]),
            CategoryDefinition("events", "🎓 EVENTS", "🎓", 2, [
                ChannelDefinition("study_sessions", "study-sessions", "text", "Organize group study"),
                ChannelDefinition("tutoring", "tutoring", "text", "Tutoring schedules"),
                ChannelDefinition("exam_prep", "exam-prep", "text", "Test preparation")
            ]),
            CategoryDefinition("study_rooms", "📝 STUDY ROOMS", "📝", 3, [
                ChannelDefinition("study_room_1", "Study Room 1", "voice", user_limit=4),
                ChannelDefinition("study_room_2", "Study Room 2", "voice", user_limit=4),
                ChannelDefinition("study_room_3", "Study Room 3", "voice", user_limit=4),
                ChannelDefinition("study_room_4", "Study Room 4", "voice", user_limit=4),
                ChannelDefinition("library", "Library (Silent)", "voice", user_limit=0)
            ])
        ]
    
    @property
    def permissions(self) -> dict[str, dict[str, PermissionOverwriteDefinition]]:
        return {
            "library": {
                "@everyone": PermissionOverwriteDefinition("@everyone", ["connect", "view_channel"], ["speak"])
            }
        }
    
    @property
    def automod_rules(self) -> list[dict]:
        return []
    
    @property
    def features(self) -> dict[str, bool]:
        return {
            "COMMUNITY": False
        }
