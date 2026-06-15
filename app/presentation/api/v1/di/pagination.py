from typing import Annotated

from fastapi import Depends

from app.presentation.api.v1.pagination.cursor_paginator import CursorPaginator as cursor_paginator

CursorPaginator = Annotated[cursor_paginator, Depends()]
