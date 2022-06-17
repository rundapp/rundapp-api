from typing import List, Optional

from databases import Database
from sqlalchemy import and_, delete

from app.infrastructure.db.models.example import BLOCKS, USERS
from app.usecases.interfaces.example import IExampleRepo
from app.usecases.schemas import example


class ExampleRepo(IExampleRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(
        self, new_user: example.UserCreate, password_context: str
    ) -> example.UserInDB:

        create_user_insert_stmt = USERS.insert().values(
            email=new_user.email,
            username=new_user.username,
            hashed_password="hashed_password",
            gender=new_user.gender,
            birthdate=new_user.birthdate,
            is_active=True,
            is_superuser=False,
            is_verified=False,
        )

        await self.db.execute(create_user_insert_stmt)

        return await self.retrieve_user_with_filter(username=new_user.username)

    async def retrieve_user_with_filter(
        self,
        user_id: str = None,
        email: str = None,
        username: str = None,
    ) -> Optional[example.UserInDB]:

        conditions = []

        if user_id:
            conditions.append(USERS.c.user_id == user_id)

        if email:
            conditions.append(USERS.c.email == email)

        if username:
            conditions.append(USERS.c.username == username)

        if len(conditions) == 0:
            raise Exception(
                "Please pass a parameter to query by to the function, retrieve_user_with_filter()"
            )

        query = USERS.select().where(and_(*conditions))

        result = await self.db.fetch_one(query)
        return example.UserInDB(**result) if result else None

    async def update(
        self,
        updated_user: example.UserUpdate,
        user_id: str,
        password_context: str,
    ) -> example.UserInDB:

        if updated_user.password:
            hashed_password = password_context.hash(updated_user.password)
            updated_user.password = hashed_password

        query = USERS.update()

        updated_user_raw = updated_user.dict()
        updated_user_raw["hashed_password"] = updated_user.password
        del updated_user_raw["password"]
        update_user_dict = {}

        for key, value in updated_user_raw.items():
            if value is not None:
                update_user_dict[key] = value

        query = query.values(update_user_dict)

        user_update_stmt = query.where(USERS.c.user_id == user_id)

        await self.db.execute(user_update_stmt)

        return await self.retrieve_user_with_filter(user_id=user_id)

    async def add_block(
        self,
        initiating_user_id: str,
        receiving_user_id: str,
    ) -> None:
        """Add block."""

        create_block_insert_stmt = BLOCKS.insert().values(
            user_id=initiating_user_id, blocked_user_id=receiving_user_id
        )

        await self.db.execute(create_block_insert_stmt)

    async def remove_block(
        self,
        initiating_user_id: str,
        receiving_user_id: str,
    ) -> None:
        """Remove block."""

        delete_statement = delete(BLOCKS).where(
            and_(
                BLOCKS.c.user_id == initiating_user_id,
                BLOCKS.c.blocked_user_id == receiving_user_id,
            )
        )

        await self.db.execute(delete_statement)

    async def retrieve_blocks(
        self,
        initiating_user_id: Optional[str] = None,
        receiving_user_id: Optional[str] = None,
    ) -> Optional[List[example.BlockInDb]]:
        """Retrieve blocks."""

        conditions = []

        if initiating_user_id:
            conditions.append(BLOCKS.c.user_id == initiating_user_id)

        if receiving_user_id:
            conditions.append(BLOCKS.c.blocked_user_id == receiving_user_id)

        query = BLOCKS.select().where(and_(*conditions))

        results = await self.db.fetch_all(query)

        return [example.BlockInDb(**result) for result in results] if results else []
