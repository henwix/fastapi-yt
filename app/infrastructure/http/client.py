from dataclasses import dataclass
from typing import Any

import httpx

from app.application.common.interfaces.http_client import IHttpClient
from app.domain.common.exceptions.http import HttpRequestError, HttpResponseError


@dataclass
class HttpxClient(IHttpClient):
    _httpx_client: httpx.AsyncClient

    async def _request(
        self,
        method: str,
        url: str,
        params: dict | None = None,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        try:
            response = await self._httpx_client.request(
                method=method,
                url=url,
                params=params,
                data=data,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HttpRequestError(url=url, method=method, exc_details=str(e)) from e
        except httpx.HTTPStatusError as e:
            response = e.response
            raise HttpResponseError(
                url=url,
                method=method,
                exc_details=str(e),
                status_code=response.status_code,
            ) from e

    async def get(
        self,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        return await self._request(method='get', url=url, params=params, headers=headers)

    async def post(
        self,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        data: dict | None = None,
    ) -> Any:
        return await self._request(method='post', url=url, params=params, headers=headers, data=data)
