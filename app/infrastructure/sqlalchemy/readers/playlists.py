from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.pagination import CursorPagination
from app.application.common.sorting import SortingOrderEnum
from app.application.playlists.dto import DetailedPlaylistDTO, PreviewPlaylistDTO
from app.application.playlists.interfaces.reader import IPlaylistReader
from app.application.playlists.queries import PlaylistsPreviewSorting
from app.domain.playlists.enums import PlaylistPrivacyStatusEnum
from app.domain.playlists.exceptions import PlaylistNotFoundError
from app.infrastructure.sqlalchemy.converters.playlists import (
    convert_playlist_row_to_detailed_dto,
    convert_playlist_row_to_preview_dto,
)
from app.infrastructure.sqlalchemy.models.channels import ChannelORM
from app.infrastructure.sqlalchemy.models.videos import PlaylistItemORM, PlaylistORM


@dataclass
class SAPlaylistReader(IPlaylistReader):
    _session: AsyncSession

    async def _get_playlists_preview(
        self,
        *filters,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: PlaylistsPreviewSorting,
        pagination: CursorPagination,
    ):
        videos_count_subquery = (
            select(sa.func.count(PlaylistItemORM.playlist_id))
            .where(PlaylistItemORM.playlist_id == PlaylistORM.id)
            .correlate(PlaylistORM)
            .scalar_subquery()
        )
        stmt = select(
            PlaylistORM.id,
            PlaylistORM.title,
            PlaylistORM.privacy_status,
            PlaylistORM.created_at,
            videos_count_subquery.label('videos_count'),
        ).where(*filters)

        sort_field = getattr(PlaylistORM, sorting.sort_by.value)

        if cursor_id_value and cursor_sort_value:
            cursor_tuple = tuple_(sort_field, PlaylistORM.id)

            if sorting.order is SortingOrderEnum.DESC:
                stmt = stmt.where(cursor_tuple < (cursor_sort_value, cursor_id_value))
            else:
                stmt = stmt.where(cursor_tuple > (cursor_sort_value, cursor_id_value))

        stmt = stmt.order_by(
            sort_field.desc() if sorting.order is SortingOrderEnum.DESC else sort_field,
            PlaylistORM.id.desc() if sorting.order is SortingOrderEnum.DESC else PlaylistORM.id,
        )

        stmt = stmt.limit(limit=pagination.per_page + 1)

        result = await self._session.execute(statement=stmt)
        playlist_rows = result.mappings().all()
        return [convert_playlist_row_to_preview_dto(row=row) for row in playlist_rows]

    async def try_get_detailed_playlist_by_id(self, id: UUID) -> DetailedPlaylistDTO:
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

        return convert_playlist_row_to_detailed_dto(row=playlist_row)

    async def get_personal_playlists(
        self,
        channel_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: PlaylistsPreviewSorting,
        pagination: CursorPagination,
    ) -> list[PreviewPlaylistDTO]:
        return await self._get_playlists_preview(
            PlaylistORM.channel_id == channel_id,
            cursor_sort_value=cursor_sort_value,
            cursor_id_value=cursor_id_value,
            sorting=sorting,
            pagination=pagination,
        )

    async def get_public_playlist_by_channel_id(
        self,
        channel_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: PlaylistsPreviewSorting,
        pagination: CursorPagination,
    ) -> list[PreviewPlaylistDTO]:
        return await self._get_playlists_preview(
            PlaylistORM.channel_id == channel_id,
            PlaylistORM.privacy_status == PlaylistPrivacyStatusEnum.PUBLIC.value,
            cursor_sort_value=cursor_sort_value,
            cursor_id_value=cursor_id_value,
            sorting=sorting,
            pagination=pagination,
        )
