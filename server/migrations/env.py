import logging
from logging.config import fileConfig

from alembic import context
from flask import current_app

config = context.config

# Set up Python logging from the alembic.ini file
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

# Point Alembic at the same database the Flask app uses.
# '%' is escaped because alembic.ini values go through string interpolation.
db = current_app.extensions["migrate"].db
config.set_main_option(
    "sqlalchemy.url",
    str(db.engine.url).replace("%", "%%"),
)


def get_metadata():
    """Return the table metadata Alembic compares against the database."""
    if hasattr(db, "metadatas"):
        return db.metadatas[None]
    return db.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    Configures the context with just a URL (no Engine), so no live database
    connection is needed. Migration SQL is emitted as script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    Creates an Engine and associates a connection with the context.
    """

    def process_revision_directives(context, revision, directives):
        # Skip generating an empty migration file when nothing has changed.
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("No changes in schema detected.")

    with db.engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            process_revision_directives=process_revision_directives,
            **current_app.extensions["migrate"].configure_args,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()