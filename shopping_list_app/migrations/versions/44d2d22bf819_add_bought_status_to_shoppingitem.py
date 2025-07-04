"""Add bought status to ShoppingItem

Revision ID: 44d2d22bf819
Revises: fc2f138a8d4d
Create Date: 2025-06-15 20:54:26.024425

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '44d2d22bf819'
down_revision = 'fc2f138a8d4d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shopping_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('bought', sa.Boolean(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('shopping_items', schema=None) as batch_op:
        batch_op.drop_column('bought')

    # ### end Alembic commands ###
