import sqlalchemy as sa

from app.infrastructure.db.metadata import METADATA

STRAVA_ACCESS = sa.Table(
    "strava_access",
    METADATA,
    sa.Column("athlete_id", sa.Integer, primary_key=True),
    sa.Column(
        "user_id",
        sa.Integer,
        sa.ForeignKey("users.id"),
        index=True,
    ),
    sa.Column("access_token", sa.String, nullable=False),
    sa.Column("refresh_token", sa.String, nullable=False),
    sa.Column("scope", sa.ARRAY(sa.String), nullable=False),
    sa.Column("expires_at", sa.Integer, nullable=False),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
)
