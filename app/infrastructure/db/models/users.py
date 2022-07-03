import sqlalchemy as sa

from app.infrastructure.db.metadata import METADATA

USERS = sa.Table(
    "users",
    METADATA,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("email", sa.String, nullable=False, unique=True, index=True),
    sa.Column("address", sa.String, nullable=True, unique=True, index=True),
    sa.Column("name", sa.String, nullable=True),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
)
