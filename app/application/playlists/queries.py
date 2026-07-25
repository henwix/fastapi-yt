from dataclasses import dataclass
from uuid import UUID


@dataclass(kw_only=True, frozen=True)
class GetPlaylistQuery:
    current_channel_id: UUID | None
    playlist_id: UUID
