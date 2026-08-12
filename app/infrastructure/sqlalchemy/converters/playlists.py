from sqlalchemy import RowMapping

from app.application.playlists.dto import DetailedPlaylistDTO, PlaylistPreviewVideoDTO, PreviewPlaylistDTO
from app.domain.playlists.enums import PlaylistPrivacyStatusEnum
from app.domain.videos.enums import VideoPrivacyStatusEnum


def convert_row_to_detailed_playlist_dto(row: RowMapping) -> DetailedPlaylistDTO:
    return DetailedPlaylistDTO(
        id=row.id,
        title=row.title,
        description=row.description,
        privacy_status=PlaylistPrivacyStatusEnum(row.privacy_status),
        created_at=row.created_at,
        author_name=row.author_name,
        author_slug=row.author_slug,
        videos_count=row.videos_count,
    )


def convert_row_to_preview_playlist_dto(row: RowMapping) -> PreviewPlaylistDTO:
    return PreviewPlaylistDTO(
        id=row.id,
        title=row.title,
        privacy_status=PlaylistPrivacyStatusEnum(row.privacy_status),
        created_at=row.created_at,
        videos_count=row.videos_count,
    )


def convert_row_to_playlist_preview_video_dto(row: RowMapping) -> PlaylistPreviewVideoDTO:
    return PlaylistPreviewVideoDTO(
        id=row.id,
        title=row.title,
        privacy_status=VideoPrivacyStatusEnum(row.privacy_status),
        created_at=row.created_at,
        views_count=row.views_count,
        added_at=row.added_at,
        author_name=row.author_name,
        author_slug=row.author_slug,
    )
