from typing import Annotated

from fastapi import Path

from app.domain.videos.constants import VIDEO_ID_PATTERN

PathVideoId = Annotated[str, Path(pattern=VIDEO_ID_PATTERN)]
