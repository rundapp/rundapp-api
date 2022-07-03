from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional

from app.usecases.schemas.strava import RefreshTokenResponse, TokenExchangeResponse


class IStravaClient(ABC):
    @abstractmethod
    async def api_call(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Mapping[str, str]] = None,
        params: Optional[Mapping[str, str]] = None,
        json_body: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """Makes API call."""

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> RefreshTokenResponse:
        """Refreshes an access token."""

    @abstractmethod
    async def get_activity(
        self, access_token: str, activity_id: int
    ) -> Mapping[str, Any]:
        """Retrieves an activity."""

    @abstractmethod
    async def exhange_code_for_token(self, code: str) -> TokenExchangeResponse:
        """Exchanges code recieved from Strava for athlete's access token."""
