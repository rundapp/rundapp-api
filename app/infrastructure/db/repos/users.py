from typing import Optional

from databases import Database
from sqlalchemy import and_

from app.infrastructure.db.models.users import USERS
from app.usecases.interfaces.repos.users import IUsersRepo
from app.usecases.schemas.users import UserBase, UserInDb


class UsersRepo(IUsersRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(self, new_user: UserBase) -> UserInDb:
        """Inserts and returns new user object."""

        insert_statement = USERS.insert().values(
            email=new_user.email,
            address=new_user.address,
        )

        id = await self.db.execute(insert_statement)

        return await self.retrieve(id=id)

    async def retrieve(
        self,
        id: Optional[int] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
    ) -> Optional[UserInDb]:
        """Retreives and returns a user object."""

        query_conditions = []

        if id:
            query_conditions.append(USERS.c.id == id)

        if email:
            query_conditions.append(USERS.c.email == email)

        if address:
            query_conditions.append(USERS.c.address == address)

        if len(query_conditions) == 0:
            raise Exception(
                "Please pass a condition parameter to query by to the function, retrieve()"
            )

        query = USERS.select().where(and_(*query_conditions))

        result = await self.db.fetch_one(query)
        return UserInDb(**result) if result else None

    async def update(self, id: int, address: str) -> UserInDb:
        """Retroactively updates user object to include address."""

        update_statement = (
            USERS.update().values(address=address).where(USERS.c.id == id)
        )

        id = await self.db.execute(update_statement)

        return await self.retrieve(id=id)
