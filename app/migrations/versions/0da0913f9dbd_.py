"""Adds column to track registration methods

Revision ID: 0da0913f9dbd
Revises: 6d8a938930ff
Create Date: 2020-04-23 14:14:24.039890

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0da0913f9dbd'
down_revision = '6d8a938930ff'
branch_labels = None
depends_on = None

registration_method = sa.Enum('USSD_SIGNUP', 'WEB_SIGNUP', name='registrationmethodenum')


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    registration_method.create(op.get_bind(), checkfirst=False)
    op.add_column('user', sa.Column('registration_method', registration_method, nullable=True))
    op.execute('ALTER TABLE "user" ALTER COLUMN registration_method TYPE registrationmethodenum'
               ' USING registration_method::text::registrationmethodenum')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'registration_method')
    registration_method.drop(op.get_bind(), checkfirst=False)
    # ### end Alembic commands ###