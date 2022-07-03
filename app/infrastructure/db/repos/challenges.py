from typing import List, Optional

from databases import Database
from sqlalchemy import and_, select

from app.infrastructure.db.models.challenges import CHALLENGES, PAYMENTS
from app.infrastructure.db.models.users import USERS
from app.usecases.interfaces.repos.challenges import IChallengesRepo
from app.usecases.schemas.challenges import (
    ChallengeBase,
    ChallengeJoinPayment,
    ChallengeJoinPaymentAndUsers,
    RetrieveChallengesAdapter,
)


class ChallengesRepo(IChallengesRepo):
    def __init__(self, db: Database):
        self.db = db

    async def create(self, new_challenge: ChallengeBase) -> ChallengeJoinPayment:
        """Inserts and returns new challenge (and payment) object."""

        insert_statement = CHALLENGES.insert().values(
            challenger=new_challenge.challenger,
            challengee=new_challenge.challengee,
            reweard=new_challenge.bounty,
            distance=new_challenge.distance,
            pace=new_challenge.pace,
            # complete=Flase, do we need this?
        )

        async with self.db.transaction():

            id = await self.db.execute(insert_statement)

            insert_statement = PAYMENTS.insert().values(
                challenge_id=id,
                # complete=False, do we need this?
            )

            await self.db.execute(insert_statement)

        return await self.retrieve(id=id)

    async def retrieve(
        self,
        id: int,
    ) -> Optional[ChallengeJoinPayment]:
        """Retreives challenge object with payment information by id."""

        j = CHALLENGES.join(PAYMENTS, CHALLENGES.c.id == PAYMENTS.c.challenge_id)

        columns_to_select = [
            CHALLENGES,
            PAYMENTS.c.id.label("payment_id"),
            PAYMENTS.c.complete.label("payment_complete"),
        ]

        query = select(columns_to_select).select_from(j).where(CHALLENGES.c.id == id)

        result = await self.db.fetch_one(query)

        return ChallengeJoinPayment(**result) if result else None

    async def retrieve_many(
        self,
        query_params: RetrieveChallengesAdapter,
    ) -> List[ChallengeJoinPaymentAndUsers]:
        """Retreives challenge objects by specified query parameters."""

        query_conditions = []

        if query_params.challengee_user_id:
            query_conditions.append(
                CHALLENGES.c.challengee == query_params.challengee_user_id
            )

        if query_params.challenger_user_id:
            query_conditions.append(
                CHALLENGES.c.challenger == query_params.challenger_user_id
            )

        if query_params.challengee_address:
            query_conditions.append(USERS.c.address == query_params.challengee_address)

        if query_params.challenger_address:
            query_conditions.append(USERS.c.address == query_params.challenger_address)

        if query_params.challenge_complete:
            query_conditions.append(
                CHALLENGES.c.complete == query_params.challenge_complete
            )

        if query_params.payment_complete:
            query_conditions.append(
                PAYMENTS.c.complete == query_params.payment_complete
            )

        if len(query_conditions) == 0:
            raise Exception(
                "Please pass a condition parameter to query by to the function, retrieve_many()"
            )

        j = CHALLENGES.join(PAYMENTS, CHALLENGES.c.id == PAYMENTS.c.challenge_id).join(
            USERS, CHALLENGES.c.challengee == USERS.c.id
        )

        columns_to_select = [
            CHALLENGES,
            USERS.c.address,
            PAYMENTS.c.id.label("payment_id"),
            PAYMENTS.c.complete.label("payment_complete"),
        ]

        query = select(columns_to_select).select_from(j).where(and_(*query_conditions))

        results = await self.db.fetch_all(query)

        return [ChallengeJoinPaymentAndUsers(**result) for result in results]

    async def update_challenge(self, id: int) -> ChallengeJoinPayment:
        """Marks a challenge as complete."""

        update_statement = (
            CHALLENGES.update().values(complete=True).where(CHALLENGES.c.id == id)
        )

        id = await self.db.execute(update_statement)
        return await self.retrieve(id=id)

    async def update_payment(self, id: int) -> None:
        """Marks a payment as complete."""

        update_statement = (
            PAYMENTS.update().values(complete=True).where(PAYMENTS.c.id == id)
        )

        await self.db.execute(update_statement)
