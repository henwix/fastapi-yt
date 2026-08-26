from dataclasses import dataclass

import httpx

from app.domain.common.exceptions import HttpRequestError, HttpResponseError
from app.infrastructure.http.base import IHttpClient


@dataclass
class HttpxHttpClient(IHttpClient):
    _httpx_client: httpx.AsyncClient

    async def _request(
        self,
        method: str,
        url: str,
        params: dict | None = None,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> dict:
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
            )

    async def get(
        self,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> dict:
        return await self._request(method='get', url=url, params=params, headers=headers)

    async def post(
        self,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        data: dict | None = None,
    ) -> dict:
        return await self._request(method='post', url=url, params=params, headers=headers, data=data)
