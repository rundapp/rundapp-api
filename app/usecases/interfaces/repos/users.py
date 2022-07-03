from abc import ABC, abstractmethod
from typing import Optional

from app.usecases.schemas.users import UserBase, UserInDb


class IUsersRepo(ABC):
    @abstractmethod
    async def create(self, new_user: UserBase) -> UserInDb:
        """Inserts user object."""

    @abstractmethod
    async def retrieve(
        self,
        id: Optional[int] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
    ) -> Optional[UserInDb]:
        """Retreives and returns a user object."""

    @abstractmethod
    async def update(self, id: int, address: str) -> UserInDb:
        """Updates user object."""
