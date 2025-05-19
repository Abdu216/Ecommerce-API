import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from urllib.parse import quote_plus

from alembic import context

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import the SQLAlchemy database configuration
from app.core.config import settings
from app.db.base_class import Base
from app.db.models import *  # Import all models

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

def get_url():
    user = settings.MYSQL_USER
    password = quote_plus(settings.MYSQL_PASSWORD)
    host = settings.MYSQL_HOST
    port = settings.MYSQL_PORT
    db = settings.MYSQL_DATABASE
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = {
        'sqlalchemy.url': get_url()
    }
    
    connectable = engine_from_config(
        configuration,
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
