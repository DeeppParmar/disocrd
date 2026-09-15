"""ID mapping utility."""
import discord

class IDMapper:
    __slots__ = ("_mapping",)

    def __init__(self) -> None:
        self._mapping: dict[int, int] = {}

    def register(self, old_id: int, new_id: int) -> None:
        self._mapping[old_id] = new_id

    def resolve(self, old_id: int) -> int:
        if old_id not in self._mapping:
            raise KeyError(f"ID {old_id} not found in mapping.")
        return self._mapping[old_id]

    def resolve_optional(self, old_id: int) -> int | None:
        return self._mapping.get(old_id)

    def remap_overwrites(self, overwrites: dict[discord.Object | discord.Role | discord.Member, discord.PermissionOverwrite]) -> dict[discord.Object, discord.PermissionOverwrite]:
        remapped: dict[discord.Object, discord.PermissionOverwrite] = {}
        for target, overwrite in overwrites.items():
            new_id = self.resolve_optional(target.id)
            if new_id is not None:
                remapped[discord.Object(id=new_id)] = overwrite
            else:
                remapped[discord.Object(id=target.id)] = overwrite
        return remapped

    def to_dict(self) -> dict[int, int]:
        return self._mapping.copy()

    def from_dict(self, data: dict[int, int]) -> None:
        self._mapping.update(data)

    def __len__(self) -> int:
        return len(self._mapping)

    def __contains__(self, item: int) -> bool:
        return item in self._mapping
