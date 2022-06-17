
from abc import ABC, abstractmethod
from typing import List, Optional
from app.usecases.schemas import example


class IExampleRepo(ABC):
    @abstractmethod
    async def create(
        self, new_user: example.UserCreate, password_context: str
    ) -> example.UserInDB:
        pass

    @abstractmethod
    async def retrieve_user_with_filter(
        self,
        user_id: str = None,
        email: str = None,
        username: str = None,
    ) -> Optional[example.UserInDB]:
        pass

    @abstractmethod
    async def update(
        self,
        updated_user: example.UserUpdate,
        user_id: str,
        password_context: str,
    ) -> example.UserInDB:
        pass

    @abstractmethod
    async def add_block(
        self,
        initiating_user_id: str,
        receiving_user_id: str,
    ) -> None:
        """Add block."""

    @abstractmethod
    async def remove_block(
        self,
        initiating_user_id: str,
        receiving_user_id: str,
    ) -> None:
        """Remove block."""

    @abstractmethod
    async def retrieve_blocks(
        self,
        initiating_user_id: Optional[str] = None,
        receiving_user_id: Optional[str] = None,
    ) -> Optional[List[example.BlockInDb]]:
        """Retrieve blocks."""
