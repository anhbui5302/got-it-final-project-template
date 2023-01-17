"""empty message

Revision ID: dd6ee063ed05
Revises: 1bbfbee8d582
Create Date: 2023-01-17 18:12:44.931405

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd6ee063ed05'
down_revision = '1bbfbee8d582'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('file',
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('url', sa.String(length=1024), nullable=False),
    sa.Column('type', sa.String(length=64), nullable=False),
    sa.Column('reference_type', sa.String(length=64), nullable=False),
    sa.Column('reference_id', sa.Integer(), nullable=True),
    sa.Column('expiration_time', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_file_ref_type_ref_id', 'file', ['reference_type', 'reference_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('idx_file_ref_type_ref_id', table_name='file')
    op.drop_table('file')
    # ### end Alembic commands ###