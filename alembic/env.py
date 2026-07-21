import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import get_settings
from app.db.session import Base
from app.db.url import prepare_asyncpg_url
from app.models import product, settings as settings_model  # noqa: F401  (registers models on Base.metadata)

config = context.config
settings = get_settings()

# Migraciones usan direct_url cuando está configurado, que sería la conexión
# de sesión completa que Alembic necesita para DDL. En este proyecto no está
# configurado, así que cae a database_url (que ya es el session-mode pooler
# de Supabase). Sin Supabase configurado (dev local con SQLite), también cae
# a database_url.
migration_url = settings.direct_url or settings.database_url
if not migration_url.startswith("sqlite"):
    migration_url, _connect_args = prepare_asyncpg_url(migration_url)

config.set_main_option("sqlalchemy.url", migration_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=migration_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
