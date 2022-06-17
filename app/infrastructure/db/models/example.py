import sqlalchemy as sa

from app.infrastructure.db.metadata import METADATA

USERS = sa.Table(
    "users",
    METADATA,
    sa.Column("user_id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("email", sa.String, nullable=False, unique=True, index=True),
    sa.Column("username", sa.String, nullable=False, unique=True, index=True),
    sa.Column("hashed_password", sa.String, nullable=False),
    sa.Column("gender", sa.String, nullable=False),
    sa.Column("birthdate", sa.Date, nullable=False),
    sa.Column("is_active", sa.Boolean, nullable=False, default=True),
    sa.Column("is_superuser", sa.Boolean, nullable=False, default=False),
    sa.Column("is_verified", sa.Boolean, nullable=False, default=False),
    sa.Column("created_at", sa.DateTime, nullable=False,
              server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
)


BLOCKS = sa.Table(
    "blocks",
    METADATA,
    sa.Column(
        "user_id",
        sa.Integer,
        sa.ForeignKey("users.user_id"),
        primary_key=True,
    ),
    sa.Column(
        "blocked_user_id",
        sa.Integer,
        sa.ForeignKey("users.user_id"),
        primary_key=True,
    ),
    sa.Column("created_at", sa.DateTime, nullable=False,
              server_default=sa.func.now()),
)
