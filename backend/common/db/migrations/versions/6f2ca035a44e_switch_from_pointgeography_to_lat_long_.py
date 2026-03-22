"""Switch from PointGeography to lat/long fields in dive_logs table

Revision ID: 6f2ca035a44e
Revises: 38de1d84b59c
Create Date: 2026-03-07 10:09:06.117402

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.types import UserDefinedType


class _PointGeography(UserDefinedType):
    """Inline stub of the removed PointGeography type, used only by downgrade."""

    cache_ok = True

    def get_col_spec(self, **kw: object) -> str:
        return "geography(Point, 4326)"


# revision identifiers, used by Alembic.
revision: str = "6f2ca035a44e"
down_revision: Union[str, None] = "38de1d84b59c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("dive_logs", "location")
    op.add_column(
        "dive_logs", sa.Column("lat", sa.DECIMAL(precision=9, scale=6), nullable=True)
    )
    op.add_column(
        "dive_logs", sa.Column("long", sa.DECIMAL(precision=9, scale=6), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("dive_logs", "long")
    op.drop_column("dive_logs", "lat")
    op.add_column(
        "dive_logs",
        sa.Column("location", _PointGeography(), nullable=True),
    )
