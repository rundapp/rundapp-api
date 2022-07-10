from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.dependencies import logger
from app.settings import settings
from app.usecases.interfaces.repos.strava import IStravaRepo
from app.usecases.interfaces.services.email_manager import IEmailManager
from app.usecases.schemas.challenges import ChallengeJoinPaymentAndUsers
from app.usecases.schemas.users import Participants


class EmailManager(IEmailManager):
    def __init__(self, strava_repo: IStravaRepo):
        self.strava_repo = strava_repo

    async def send(self, sender: str, recipient: str, subject: str, body: str) -> None:
        """Sends an email."""

        # 1. Construct Message.
        message = Mail(
            from_email=sender,
            to_emails=recipient,
            subject=subject,
            plain_text_content=body,
        )

        # 2. Instantiate Sendgrid Client.
        sg = SendGridAPIClient(settings.sendgrid_api_key)

        # 3. Send Message
        try:
            sg.send(message)
        except Exception as e:
            logger.exception(e)
        else:
            logger.info("[EmailManager]: Successfully sent email.")

    async def challenge_issuance_notification(
        self, participants: Participants, challenge: ChallengeJoinPaymentAndUsers
    ) -> None:
        """Notifies challenge participants."""

        # 1. Construct body.
        challenger = (
            participants.challenger.name
            if participants.challenger.name
            else participants.challenger.email
        )
        challengee = (
            participants.challengee.name
            if participants.challengee.name
            else participants.challengee.email
        )

        needs_auth = await self.__check_authorizaion(participants=participants)

        challengee_body = f"{challenger} challenged you to run {challenge.distance} miles at a {challenge.pace}/min pace. You'll receive {challenge.bounty} Ether if you complete the challenge.\n\n"
        auth_language = f"In order to complete this challenge, please provide Rundapp access to your Strava account using the following link. If you do not already have a Strava account, this same link will prompt you to create one: https://www.strava.com/oauth/authorize?client_id=88040&response_type=code&redirect_uri=https://www.rundapp.quest?user_id={participants.challengee.id}&approval_prompt=force&scope=read_all,activity:read_all"
        

        # 2. Notify Challengee.
        await self.send(
            sender=settings.sender_email_address,
            recipient=participants.challengee.email,
            subject="New bounty - you've been challenged.",
            body=(challengee_body + auth_language) if needs_auth else challengee_body,
        )

        # 3. Notify Challenger.
        await self.send(
            sender=settings.sender_email_address,
            recipient=participants.challenger.email,
            subject="You issued a challenge.",
            body=f"{challengee} has been challenged and notified via email. Challenge details:\nDistance: {challenge.distance}miles\nPace: {challenge.pace}/min pace\nBounty: {challenge.bounty} Ether",
        )

    async def __check_authorizaion(self, participants: Participants) -> bool:
        """Checks if challengee has given access to Strava."""

        strava_access = await self.strava_repo.retrieve(
            user_id=participants.challengee.id
        )

        if strava_access:
            if strava_access.scope:
                return False
            else:
                return True
        else:
            return True
