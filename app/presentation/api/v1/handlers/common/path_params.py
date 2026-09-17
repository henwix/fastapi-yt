from typing import Annotated

from fastapi import Path

from app.domain.common.constants import SLUG_PATTERN
from app.domain.videos.constants import VIDEO_ID_PATTERN

PathVideoId = Annotated[str, Path(pattern=VIDEO_ID_PATTERN)]
PathChannelSlug = Annotated[str, Path(min_length=1, max_length=40, pattern=SLUG_PATTERN)]
