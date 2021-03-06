"""empty message

Revision ID: 0a0e0257f303
Revises: c751b5d5bad9
Create Date: 2018-09-23 19:07:54.456689

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a0e0257f303'
down_revision = 'c751b5d5bad9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('_is_subvendor', sa.Boolean(), nullable=True))
    op.drop_column('user', '_is_supervendor')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('_is_supervendor', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('user', '_is_subvendor')
    # ### end Alembic commands ###
