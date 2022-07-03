from typing import Any, Mapping, Optional

import aiohttp

from app.settings import settings
from app.usecases.interfaces.clients.strava import IStravaClient
from app.usecases.schemas.strava import (
    RefreshTokenResponse,
    StravaException,
    TokenExchangeResponse,
)


class StravaClient(IStravaClient):
    """Faciliates communication with Strava's API."""

    def __init__(self, client_session: aiohttp.client.ClientSession, base_url: str):
        self.client_session = client_session
        self.base_url = base_url

    async def api_call(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Mapping[str, str]] = None,
        params: Optional[Mapping[str, str]] = None,
        json_body: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """Make API call."""

        async with self.client_session.request(
            method,
            self.base_url + endpoint,
            headers=headers,
            json=json_body,
            params=params,
            verify_ssl=False,
        ) as response:
            try:
                return await response.json()
            except Exception:
                response_text = await response.text()
                raise StravaException(  # pylint: disable=raise-missing-from
                    f"Strava Client Error: Response status: {response.status}, Response Text: {response_text}"
                )

    async def refresh_token(self, refresh_token: str) -> RefreshTokenResponse:
        """Refreshes a Strava athlete's access token."""

        response = await self.api_call(
            method="POST",
            endpoint="/oauth/token",
            params={
                "client_id": settings.client_id,
                "client_secret": settings.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
        )

        return RefreshTokenResponse(**response)

    async def exhange_code_for_token(self, code: str) -> TokenExchangeResponse:
        """Exchanges code recieved from Strava for athlete's access token."""

        response = await self.api_call(
            method="POST",
            endpoint="/oauth/token",
            params={
                "client_id": settings.client_id,
                "client_secret": settings.client_secret,
                "grant_type": "authorization_code",
                "code": code,
            },
        )

        return TokenExchangeResponse(**response)

    async def get_activity(
        self, access_token: str, activity_id: int
    ) -> Mapping[str, Any]:
        """Retrieves a Strava athlete's activity. Returns a massive JSON response."""

        return await self.api_call(
            method="GET",
            endpoint=f"/activities/{activity_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
