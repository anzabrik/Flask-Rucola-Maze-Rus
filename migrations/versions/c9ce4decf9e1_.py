"""empty message

Revision ID: c9ce4decf9e1
Revises: cbe73dcd5912
Create Date: 2023-11-27 19:53:04.744940

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9ce4decf9e1'
down_revision = 'cbe73dcd5912'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('menu_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('price_dollars', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('price_cents', sa.Integer(), nullable=True))
        batch_op.drop_column('price')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('menu_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('price', sa.INTEGER(), nullable=True))
        batch_op.drop_column('price_cents')
        batch_op.drop_column('price_dollars')

    # ### end Alembic commands ###