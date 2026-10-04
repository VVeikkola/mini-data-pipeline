import logging

from config import COMBINED_CSV_PATH
from db import get_connection
from ingest import read_raw_csv
from transform import transform
from validate import validate

logger = logging.getLogger(__name__)

# Parent tables first, so foreign keys always find their target row
LOAD_ORDER = ["customers", "products", "invoices", "invoice_lines"]

REJECTED_COLUMNS = {
    "reject_reason": "reject_reason",
    "Invoice": "invoice",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "Price": "price",
    "Customer ID": "customer_id",
    "Country": "country",
}


def to_rows(df):
    """Yield rows as plain tuples with None instead of NaN."""
    clean = df.astype(object).where(df.notna(), None)
    return clean.itertuples(index=False, name=None)


def copy_table(cur, table, df):
    """Bulk load a DataFrame into a table with COPY."""
    columns = ", ".join(df.columns)
    with cur.copy(f"COPY {table} ({columns}) FROM STDIN") as copy:
        for row in to_rows(df):
            copy.write_row(row)
    logger.info("Loaded %d rows into %s", len(df), table)


def load(tables, rejected):
    """Replace all data in one transaction. Re-running gives the same result."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "TRUNCATE invoice_lines, invoices, products, customers, rejected_rows "
                "RESTART IDENTITY"
            )
            for table in LOAD_ORDER:
                copy_table(cur, table, tables[table])

            rejected_out = rejected[list(REJECTED_COLUMNS)].rename(
                columns=REJECTED_COLUMNS
            )
            copy_table(cur, "rejected_rows", rejected_out)


def main():
    valid, rejected = validate(read_raw_csv(COMBINED_CSV_PATH))
    tables = transform(valid)
    load(tables, rejected)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    main()
