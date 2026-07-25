from dataclasses import dataclass
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.playlists.dto import DetailedPlaylistDTO
from app.application.playlists.interfaces.reader import IPlaylistReader
from app.domain.playlists.exceptions import PlaylistNotFoundError
from app.infrastructure.sqlalchemy.converters.playlists import convert_playlist_row_to_dto
from app.infrastructure.sqlalchemy.models.channels import ChannelORM
from app.infrastructure.sqlalchemy.models.videos import PlaylistItemORM, PlaylistORM


@dataclass
class SAPlaylistReader(IPlaylistReader):
    _session: AsyncSession

    async def try_get_detailed_by_id(self, id: UUID) -> DetailedPlaylistDTO:
        videos_count_subquery = (
            select(sa.func.count(PlaylistItemORM.playlist_id))
            .where(
                PlaylistItemORM.playlist_id == id,
            )
            .scalar_subquery()
        )

        stmt = (
            select(
                PlaylistORM.id,
                PlaylistORM.title,
                PlaylistORM.description,
                PlaylistORM.privacy_status,
                PlaylistORM.created_at,
                ChannelORM.name.label('author_name'),
                ChannelORM.slug.label('author_slug'),
                videos_count_subquery.label('videos_count'),
            )
            .join(ChannelORM, PlaylistORM.channel_id == ChannelORM.id)
            .where(PlaylistORM.id == id)
        )
        result = await self._session.execute(statement=stmt)
        playlist_row = result.mappings().one_or_none()

        if playlist_row is None:
            raise PlaylistNotFoundError(playlist_id=id)

        return convert_playlist_row_to_dto(row=playlist_row)
