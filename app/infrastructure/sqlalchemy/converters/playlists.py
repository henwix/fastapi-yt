from sqlalchemy import RowMapping

from app.application.playlists.dto import DetailedPlaylistDTO, PreviewPlaylistDTO
from app.domain.playlists.enums import PlaylistPrivacyStatusEnum


def convert_playlist_row_to_detailed_dto(row: RowMapping) -> DetailedPlaylistDTO:
    return DetailedPlaylistDTO(
        id=row['id'],
        title=row['title'],
        description=row['description'],
        privacy_status=PlaylistPrivacyStatusEnum(row['privacy_status']),
        created_at=row['created_at'],
        author_name=row['author_name'],
        author_slug=row['author_slug'],
        videos_count=row['videos_count'],
    )


def convert_playlist_row_to_preview_dto(row: RowMapping) -> PreviewPlaylistDTO:
    return PreviewPlaylistDTO(
        id=row['id'],
        title=row['title'],
        privacy_status=PlaylistPrivacyStatusEnum(row['privacy_status']),
        created_at=row['created_at'],
        videos_count=row['videos_count'],
    )
