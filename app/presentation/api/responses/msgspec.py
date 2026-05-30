from typing import Any

import msgspec
from fastapi.responses import JSONResponse


class MsgSpecJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes | memoryview:
        assert msgspec is not None, 'msgspec must be installed'
        return msgspec.json.encode(content)
