from sqlalchemy import RowMapping

from app.application.playlists.dto import DetailedPlaylist, PlaylistPreviewVideo, PreviewPlaylist
from app.core.configs import settings
from app.domain.playlists.enums import PlaylistPrivacyStatusEnum
from app.domain.videos.enums import VideoPrivacyStatusEnum


def convert_row_to_detailed_playlist_dto(row: RowMapping) -> DetailedPlaylist:
    return DetailedPlaylist(
        id=row.id,
        title=row.title,
        description=row.description,
        privacy_status=PlaylistPrivacyStatusEnum(row.privacy_status),
        created_at=row.created_at,
        channel_name=row.channel_name,
        channel_slug=row.channel_slug,
        channel_avatar_url=f'{settings.s3_public_bucket_url}/{row.channel_avatar_key}'
        if row.channel_avatar_key
        else None,
    )


def convert_row_to_preview_playlist_dto(row: RowMapping) -> PreviewPlaylist:
    return PreviewPlaylist(
        id=row.id,
        title=row.title,
        privacy_status=PlaylistPrivacyStatusEnum(row.privacy_status),
        created_at=row.created_at,
    )


def convert_row_to_playlist_preview_video_dto(row: RowMapping) -> PlaylistPreviewVideo:
    return PlaylistPreviewVideo(
        id=row.id,
        title=row.title,
        privacy_status=VideoPrivacyStatusEnum(row.privacy_status),
        created_at=row.created_at,
        views_count=row.views_count,
        added_at=row.added_at,
        channel_name=row.channel_name,
        channel_slug=row.channel_slug,
        video_thumbnail_url=f'{settings.s3_public_bucket_url}/{row.video_thumbnail_key}'
        if row.video_thumbnail_key
        else None,
    )
