import logging

import pandas as pd

from config import COMBINED_CSV_PATH

logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = [
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country",
]


def read_raw_csv(path):
    """Read every column as text. Types are checked in validation."""
    df = pd.read_csv(path, dtype=str, keep_default_na=False, na_values=[""])

    if list(df.columns) != EXPECTED_COLUMNS:
        raise ValueError(
            f"Unexpected columns in {path}: {list(df.columns)}, expected {EXPECTED_COLUMNS}"
        )
    if df.empty:
        raise ValueError(f"No rows in {path}")

    logger.info("Read %d rows from %s", len(df), path)
    return df


def main():
    df = read_raw_csv(COMBINED_CSV_PATH)
    logger.info("Column types: %s", df.dtypes.to_dict())


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    main()
