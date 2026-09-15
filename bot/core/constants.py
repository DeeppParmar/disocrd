"""Constants and enumerations for the bot core."""

from enum import Enum, auto
import discord


class PermissionPreset(Enum):
    """Permission presets for different role tiers."""
    OWNER = discord.Permissions.all()
    ADMINISTRATOR = discord.Permissions(administrator=True)
    MODERATOR = discord.Permissions(
        manage_channels=True,
        manage_roles=True,
        manage_webhooks=True,
        manage_messages=True,
        manage_threads=True,
        moderate_members=True,
        kick_members=True,
        ban_members=True,
        view_audit_log=True,
        mute_members=True,
        deafen_members=True,
        move_members=True
    )
    SUPPORT = discord.Permissions(
        manage_messages=True,
        manage_threads=True,
        moderate_members=True,
        mute_members=True,
        move_members=True
    )
    HELPER = discord.Permissions(
        manage_messages=True,
        manage_threads=True
    )
    MEMBER = discord.Permissions(
        send_messages=True,
        send_messages_in_threads=True,
        create_public_threads=True,
        create_private_threads=True,
        embed_links=True,
        attach_files=True,
        add_reactions=True,
        use_external_emojis=True,
        use_external_stickers=True,
        read_message_history=True,
        connect=True,
        speak=True,
        stream=True,
        use_voice_activation=True,
        change_nickname=True
    )
    BOT = discord.Permissions(
        view_channel=True,
        send_messages=True,
        embed_links=True,
        attach_files=True,
        read_message_history=True
    )
    MUTED = discord.Permissions(
        send_messages=False,
        send_messages_in_threads=False,
        create_public_threads=False,
        create_private_threads=False,
        add_reactions=False,
        speak=False,
        stream=False
    )
    QUARANTINED = discord.Permissions(
        view_channel=False
    )


class ServerType(Enum):
    """Types of server configurations."""
    COMMUNITY = auto()
    GAMING = auto()
    CREATOR = auto()
    SUPPORT = auto()
    STUDY = auto()
    BUSINESS = auto()
    FRIENDS = auto()
    CUSTOM = auto()


class SetupPhase(Enum):
    """Phases of the server setup process."""
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    ROLLED_BACK = auto()


class TicketStatus(Enum):
    """Status of support tickets."""
    OPEN = auto()
    CLAIMED = auto()
    CLOSED = auto()
    DELETED = auto()


class ModerationAction(Enum):
    """Types of moderation actions."""
    WARN = auto()
    TIMEOUT = auto()
    KICK = auto()
    BAN = auto()
    SOFTBAN = auto()
    UNBAN = auto()
    UNTIMEOUT = auto()


class Colors:
    """Standardized branded hex colors for embeds."""
    PRIMARY = 0x5865F2     # Blurple
    SUCCESS = 0x57F287     # Green
    WARNING = 0xFEE75C     # Yellow
    DANGER = 0xED4245      # Red
    INFO = 0x00AFF4        # Light Blue
    NEUTRAL = 0x2B2D31     # Dark Gray
    INVISIBLE = 0x2B2D31   # matches Discord dark theme background


class SecurityLevel(Enum):
    """Security level configurations."""
    BASIC = auto()
    BALANCED = auto()
    STRICT = auto()
    MAXIMUM = auto()
    CUSTOM = auto()


class LogCategory(Enum):
    """Categories for server logging."""
    MODERATION = auto()
    SECURITY = auto()
    MEMBERS = auto()
    ROLES = auto()
    CHANNELS = auto()
    TICKETS = auto()
    MESSAGES = auto()
    BOTS = auto()
    INVITES = auto()
    WEBHOOKS = auto()
    SERVER = auto()
    AUTOMOD = auto()
