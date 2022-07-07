import sqlalchemy as sa

from app.infrastructure.db.metadata import METADATA

CHALLENGES = sa.Table(
    "challenges",
    METADATA,
    sa.Column("id", sa.String, primary_key=True),
    sa.Column(
        "challenger",
        sa.Integer,
        sa.ForeignKey("users.id"),
        index=True,
    ),
    sa.Column(
        "challengee",
        sa.Integer,
        sa.ForeignKey("users.id"),
        index=True,
    ),
    sa.Column("bounty", sa.BigInteger, nullable=False),
    sa.Column("distance", sa.Float, nullable=False),
    sa.Column("pace", sa.Float, nullable=True),
    sa.Column("complete", sa.Boolean, nullable=False, default=False),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
)

PAYMENTS = sa.Table(
    "payments",
    METADATA,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column(
        "challenge_id",
        sa.String,
        sa.ForeignKey("challenges.id"),
        index=True,
    ),
    sa.Column("complete", sa.Boolean, nullable=False, default=False),
    sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    sa.Column(
        "updated_at",
        sa.DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    ),
)
