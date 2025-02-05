"""added area to cohort

Revision ID: 0671b732840b
Revises: e08e14de018f
Create Date: 2024-11-18 15:29:27.075487

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0671b732840b'
down_revision: Union[str, None] = 'e08e14de018f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cohorts', sa.Column('area', sa.String(length=20), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('cohorts', 'area')
    # ### end Alembic commands ###
