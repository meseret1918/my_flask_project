"""Added new fields to Job model

Revision ID: 29f75ba44eec
Revises: fcc00ea1db2d
Create Date: 2024-09-01 16:31:04.257042

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '29f75ba44eec'
down_revision = 'fcc00ea1db2d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('jobs')
    with op.batch_alter_table('job', schema=None) as batch_op:
        batch_op.add_column(sa.Column('currency', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('responsibilities', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('requirements', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('job', schema=None) as batch_op:
        batch_op.drop_column('requirements')
        batch_op.drop_column('responsibilities')
        batch_op.drop_column('currency')

    op.create_table('jobs',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('title', mysql.VARCHAR(length=250), nullable=False),
    sa.Column('location', mysql.VARCHAR(length=250), nullable=False),
    sa.Column('salary', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('currency', mysql.VARCHAR(length=10), nullable=True),
    sa.Column('responsibilities', mysql.VARCHAR(length=2000), nullable=True),
    sa.Column('requirements', mysql.VARCHAR(length=2000), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
