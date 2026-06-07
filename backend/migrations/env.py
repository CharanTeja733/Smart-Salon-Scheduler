import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
sys.path.append('/app')
from app.database import Base
from app.models import *   # Import all models to register with Base

target_metadata = Base.metadata

# ============================
# Exclude PostGIS system tables from autogenerate
# ============================
def include_object(object, name, type_, reflected, compare_to):
    """
    Exclude PostGIS spatial_ref_sys table and any other PostGIS internal tables
    from Alembic's autogenerate. Also exclude spatial indexes that are managed
    by GeoAlchemy2 (optional).
    """
    # List of known PostGIS system tables to exclude
    postgis_tables = (
        'spatial_ref_sys',
        'geography_columns',
        'geometry_columns',
        'raster_columns',
        'raster_overviews',
        'topology',
        'layer',
    )
    if type_ == 'table' and name in postgis_tables:
        return False

    # Optionally also exclude tables in the 'tiger' or 'topology' schemas
    if reflected and hasattr(object, 'schema') and object.schema in ('tiger', 'topology'):
        return False

    # Optionally exclude GiST indexes that are automatically created for PostGIS columns
    # (Uncomment if you want to exclude all GiST indexes)
    # if type_ == 'index' and reflected:
    #     if hasattr(object, 'dialect_options') and object.dialect_options.get('postgresql_using') == 'gist':
    #         return False

    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,   # <-- exclude PostGIS tables
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,   # <-- exclude PostGIS tables
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()