from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.pagination import CursorPagination
from app.application.common.sorting import SortingOrderEnum
from app.application.playlists.dto import DetailedPlaylistDTO, PlaylistPreviewVideoDTO, PreviewPlaylistDTO
from app.application.playlists.interfaces.reader import IPlaylistReader
from app.application.playlists.queries import (
    PlaylistsPreviewSorting,
    PlaylistVideosSorting,
    PlaylistVideosSortingFieldsEnum,
)
from app.domain.playlists.enums import PlaylistPrivacyStatusEnum
from app.domain.playlists.exceptions import PlaylistNotFoundError
from app.domain.videos.enums import VideoPrivacyStatusEnum
from app.infrastructure.sqlalchemy.converters.playlists import (
    convert_row_to_detailed_playlist_dto,
    convert_row_to_playlist_preview_video_dto,
    convert_row_to_preview_playlist_dto,
)
from app.infrastructure.sqlalchemy.models.channels import ChannelORM
from app.infrastructure.sqlalchemy.models.videos import PlaylistItemORM, PlaylistORM, VideoORM


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
            .join(VideoORM, PlaylistItemORM.video_id == VideoORM.id)
            .where(
                PlaylistItemORM.playlist_id == PlaylistORM.id,
                VideoORM.privacy_status.in_(
                    [
                        VideoPrivacyStatusEnum.PUBLIC.value,
                        VideoPrivacyStatusEnum.UNLISTED.value,
                    ]
                ),
            )
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
        return [convert_row_to_preview_playlist_dto(row=row) for row in playlist_rows]

    async def try_get_detailed_playlist_by_id(self, id: UUID) -> DetailedPlaylistDTO:
        videos_count_subquery = (
            select(sa.func.count(PlaylistItemORM.playlist_id))
            .join(VideoORM, PlaylistItemORM.video_id == VideoORM.id)
            .where(
                PlaylistItemORM.playlist_id == id,
                VideoORM.privacy_status.in_(
                    [
                        VideoPrivacyStatusEnum.PUBLIC.value,
                        VideoPrivacyStatusEnum.UNLISTED.value,
                    ]
                ),
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

        return convert_row_to_detailed_playlist_dto(row=playlist_row)

    async def get_playlists_by_channel_id(
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

    async def get_public_playlists_by_channel_id(
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

    async def get_playlist_videos_by_playlist_id(
        self,
        playlist_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: str | None,
        sorting: PlaylistVideosSorting,
        pagination: CursorPagination,
    ) -> list[PlaylistPreviewVideoDTO]:
        stmt = (
            select(
                PlaylistItemORM.video_id.label('id'),
                VideoORM.title,
                VideoORM.privacy_status,
                VideoORM.created_at,
                VideoORM.views_count,
                PlaylistItemORM.created_at.label('added_at'),
                ChannelORM.name.label('author_name'),
                ChannelORM.slug.label('author_slug'),
            )
            .join(VideoORM, PlaylistItemORM.video_id == VideoORM.id)
            .join(ChannelORM, VideoORM.channel_id == ChannelORM.id)
            .where(
                PlaylistItemORM.playlist_id == playlist_id,
                VideoORM.privacy_status.in_(
                    [
                        VideoPrivacyStatusEnum.PUBLIC.value,
                        VideoPrivacyStatusEnum.UNLISTED.value,
                    ]
                ),
            )
        )

        match sorting.sort_by:
            case PlaylistVideosSortingFieldsEnum.ADDED_AT:
                sort_field = PlaylistItemORM.created_at
            case PlaylistVideosSortingFieldsEnum.CREATED_AT:
                sort_field = VideoORM.created_at

        if cursor_sort_value and cursor_id_value:
            cursor_tuple = tuple_(sort_field, PlaylistItemORM.video_id)

            if sorting.order is SortingOrderEnum.DESC:
                stmt = stmt.where(cursor_tuple < (cursor_sort_value, cursor_id_value))
            else:
                stmt = stmt.where(cursor_tuple > (cursor_sort_value, cursor_id_value))

        stmt = stmt.order_by(
            sort_field.desc() if sorting.order is SortingOrderEnum.DESC else sort_field,
            PlaylistItemORM.video_id.desc() if sorting.order is SortingOrderEnum.DESC else PlaylistItemORM.video_id,
        )
        stmt = stmt.limit(limit=pagination.per_page + 1)

        result = await self._session.execute(statement=stmt)
        video_rows = result.mappings().all()
        return [convert_row_to_playlist_preview_video_dto(row=row) for row in video_rows]
