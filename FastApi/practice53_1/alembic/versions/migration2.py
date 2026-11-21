from alembic import op
import sqlalchemy as sa 
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer

revision = 'add_initial_data'
down_revision = '03517e8e43b7'
branch_labels = None
depends_on = None

users_table = table(
    'users',
    column('id', Integer),
    column('username', String),
    column('email', String),
    column('password', String)
)

def upgrade():
    op.add_column('users', sa.Column('email', sa.String(255), nullable=True))
    initial_data = [
        {'id': 1, 'username': 'admin', 'email': 'admin@example.com', 'password': 'hashed_password'},
        {'id': 2, 'username': 'user', 'email': 'user@example.com', 'password': 'hashed_password'}
    ]

    op.bulk_insert(users_table, initial_data)


def downgrade():
    op.drop_column('users', 'email')
    op.execute("DELETE FROM users WHERE username IN ('admin', 'user')")