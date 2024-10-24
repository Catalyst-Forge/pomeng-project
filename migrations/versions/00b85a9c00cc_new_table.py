"""new table

Revision ID: 00b85a9c00cc
Revises: f89ab488de10
Create Date: 2024-10-22 18:41:01.918316

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00b85a9c00cc'
down_revision = 'f89ab488de10'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('intent',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tag', sa.String(length=80), nullable=False),
    sa.Column('patterns', sa.Text(), nullable=False),
    sa.Column('responses', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('intent')
    # ### end Alembic commands ###
