"""empty message

Revision ID: 311569eda055
Revises: d5ac8e623850
Create Date: 2019-08-28 13:54:24.538147

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '311569eda055'
down_revision = 'd5ac8e623850'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('_held_roles', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.drop_column('user', '_is_view')
    op.drop_column('user', '_is_supervendor')
    op.drop_column('user', '_is_sempo_admin')
    op.drop_column('user', '_is_subadmin')
    op.drop_column('user', '_is_superadmin')
    op.drop_column('user', '_is_admin')
    op.drop_column('user', '_is_vendor')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('_is_vendor', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('_is_admin', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('_is_superadmin', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('_is_subadmin', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('_is_sempo_admin', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('_is_supervendor', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('_is_view', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('user', '_held_roles')
    # ### end Alembic commands ###
