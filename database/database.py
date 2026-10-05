import sqlite3
from pathlib import Path

from config import config


def get_database():
    """
    Create and return a SQLite database connection.

    The connection uses sqlite3.Row so database records
    can be accessed by column name.
    """
    database_path = Path(config.DATABASE_PATH)

    # Create the database directory if it does not exist.
    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        database_path,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    # Enable foreign-key constraints.
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def init_database():
    """
    Initialize the BESTORA FIT database using schema.sql.
    """
    schema_path = Path(__file__).parent / "schema.sql"

    if not schema_path.exists():
        raise FileNotFoundError(
            f"Database schema not found: {schema_path}"
        )

    connection = get_database()

    try:
        with open(schema_path, "r", encoding="utf-8") as schema_file:
            schema = schema_file.read()

        connection.executescript(schema)
        connection.commit()

    finally:
        connection.close()


def close_database(connection):
    """
    Safely close a database connection.
    """
    if connection is not None:
        connection.close() 