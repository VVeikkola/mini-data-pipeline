"""Database connection helpers."""

import logging

import psycopg

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

logger = logging.getLogger(__name__)


def get_connection():
    """Open a new connection to the pipeline database."""
    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def main():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version()")
            logger.info("Connected: %s", cur.fetchone()[0])

            cur.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = %s ORDER BY table_name",
                ("public",),
            )
            tables = [row[0] for row in cur.fetchall()]
            logger.info("Tables: %s", tables)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    main()
