from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum


class ServerType(Enum):
    COMMUNITY = "community"
    GAMING = "gaming"
    CREATOR = "creator"
    SUPPORT = "support"
    BUSINESS = "business"
    STUDY = "study"
    FRIENDS = "friends"


@dataclass(slots=True)
class RoleDefinition:
    """Defines a role within a server template."""
    logical_name: str
    display_name: str
    emoji: str
    color: int
    permissions_preset: str
    hoist: bool = False
    mentionable: bool = False
    position_priority: int = 0


@dataclass(slots=True)
class ChannelDefinition:
    """Defines a channel within a category."""
    logical_name: str
    display_name: str
    channel_type: str
    topic: str = ""
    slowmode: int = 0
    nsfw: bool = False
    bitrate: int = 64000
    user_limit: int = 0


@dataclass(slots=True)
class CategoryDefinition:
    """Defines a category and its channels."""
    logical_name: str
    display_name: str
    emoji: str
    position: int
    channels: list[ChannelDefinition] = field(default_factory=list)


@dataclass(slots=True)
class PermissionOverwriteDefinition:
    """Defines a permission overwrite for a role in a channel/category."""
    role_logical_name: str
    allow: list[str] = field(default_factory=list)
    deny: list[str] = field(default_factory=list)


class ServerTemplate(ABC):
    """Abstract base class for server templates."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the template."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Description of the template."""
        pass
    
    @property
    @abstractmethod
    def server_type(self) -> ServerType:
        """Type of the server."""
        pass
    
    @property
    @abstractmethod
    def roles(self) -> list[RoleDefinition]:
        """List of role definitions."""
        pass
    
    @property
    @abstractmethod
    def categories(self) -> list[CategoryDefinition]:
        """List of category definitions."""
        pass
    
    @property
    @abstractmethod
    def permissions(self) -> dict[str, dict[str, PermissionOverwriteDefinition]]:
        """
        Dictionary of target_logical_name (category or channel) 
        -> dict of role_logical_name -> PermissionOverwriteDefinition.
        """
        pass
    
    @property
    @abstractmethod
    def automod_rules(self) -> list[dict]:
        """List of AutoMod rule definitions."""
        pass
    
    @property
    @abstractmethod
    def features(self) -> dict[str, bool]:
        """Dictionary of server features."""
        pass
