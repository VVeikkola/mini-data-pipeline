from decimal import Decimal
from pathlib import Path

import pandas as pd
import psycopg
import pytest

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER
from db import get_connection
from load import load
from transform import transform
from validate import validate

pytestmark = pytest.mark.integration

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"


@pytest.fixture(scope="module")
def test_database():
    """Create the test database if needed and apply a fresh schema."""
    try:
        admin = psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=5,
            autocommit=True,
        )
    except psycopg.OperationalError:
        pytest.skip("PostgreSQL is not running")

    with admin:
        exists = admin.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,)
        ).fetchone()
        if not exists:
            admin.execute(f'CREATE DATABASE "{DB_NAME}"')

    with get_connection() as conn:
        conn.execute(SCHEMA_PATH.read_text())


def raw_rows():
    base = {
        "Invoice": "489434",
        "StockCode": "85048",
        "Description": "LIGHTS",
        "Quantity": "12",
        "InvoiceDate": "2009-12-01 07:45:00",
        "Price": "0.001",
        "Customer ID": "13085.0",
        "Country": "United Kingdom",
    }
    return pd.DataFrame(
        [
            base,
            {**base, "StockCode": "POST", "Description": "POSTAGE", "Price": "18.00"},
            {**base, "Invoice": "489500", "Customer ID": None},
            {**base, "Invoice": "X1"},  # rejected
        ],
        dtype="str",
    )


def run_once():
    valid, rejected = validate(raw_rows())
    load(transform(valid), rejected)
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT (SELECT count(*) FROM invoice_lines),
                   (SELECT max(line_id) FROM invoice_lines),
                   (SELECT count(*) FROM rejected_rows),
                   (SELECT sum(quantity * unit_price) FROM invoice_lines)
            """
        ).fetchone()


def test_load_is_idempotent(test_database):
    first = run_once()
    second = run_once()
    assert first == second == (3, 3, 1, Decimal("216.024"))


def test_values_survive_the_round_trip(test_database):
    run_once()
    with get_connection() as conn:
        price = conn.execute(
            "SELECT unit_price FROM invoice_lines WHERE stock_code = '85048' LIMIT 1"
        ).fetchone()[0]
        customer = conn.execute(
            "SELECT customer_id FROM invoices WHERE invoice_no = '489500'"
        ).fetchone()[0]
        row_type = conn.execute(
            "SELECT row_type FROM invoice_lines WHERE stock_code = 'POST'"
        ).fetchone()[0]

    assert price == Decimal("0.001")
    assert customer is None
    assert row_type == "non_product"
