from abc import ABC, abstractmethod

from app.usecases.schemas.strava import WebhookEvent


class IChallengeValidation(ABC):
    @abstractmethod
    async def validate(self, event: WebhookEvent) -> None:
        """Validates Challenge."""
