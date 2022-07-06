from os import path

from pydantic import BaseSettings

DOTENV_FILE = ".env" if path.isfile(".env") else None


class Settings(BaseSettings):
    """Application Settings and Environment Variables"""

    # Application Settings
    application_name: str = "rundapp"
    environment: str = "development"
    log_level: str = "info"
    server_host: str = "0.0.0.0"
    server_port: int
    server_prefix: str = ""
    openapi_url: str = "/openapi.json"

    # Database Settings
    db_url: str

    # Strava Settings
    verify_token: str
    client_id: str
    client_secret: str
    strava_base_url: str = "https://www.strava.com/api/v3"

    # Ethereum Settings
    signer_private_key: str

    # Sendgrid Settings
    sendgrid_api_key: str

    # Miscellaneous Settings
    sender_email_address: str

    class Config:
        env_file = DOTENV_FILE


settings: Settings = Settings()
