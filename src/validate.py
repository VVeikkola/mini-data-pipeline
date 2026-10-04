import logging

import pandas as pd

from config import COMBINED_CSV_PATH
from ingest import read_raw_csv

logger = logging.getLogger(__name__)

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def find_reject_reasons(raw):
    """Return the first reject reason per row, or NA if the row is valid."""
    quantity = pd.to_numeric(raw["Quantity"], errors="coerce")
    price = pd.to_numeric(raw["Price"], errors="coerce")
    invoiced_at = pd.to_datetime(
        raw["InvoiceDate"], format=TIMESTAMP_FORMAT, errors="coerce"
    )
    is_accounting = raw["Invoice"].str.startswith("A", na=False)

    rules = {
        "invalid_invoice": ~raw["Invoice"].str.fullmatch(r"[CA]?\d{6}", na=False),
        "missing_stock_code": raw["StockCode"].isna()
        | (raw["StockCode"].str.strip() == ""),
        "invalid_quantity": quantity.isna() | (quantity % 1 != 0) | (quantity == 0),
        "invalid_invoice_date": invoiced_at.isna(),
        "invalid_price": price.isna() | ((price < 0) & ~is_accounting),
    }

    reasons = pd.Series(pd.NA, index=raw.index, dtype="string")
    for reason, failed in rules.items():
        reasons = reasons.mask(reasons.isna() & failed, reason)
    return reasons


def log_warnings(valid):
    """Log WARN rules from the contract. Rows are kept."""
    checks = {
        "invoice date in the future": valid["InvoiceDate"] > pd.Timestamp.now(),
        "missing country": valid["Country"].isna(),
        "exact duplicate rows": valid.duplicated(),
    }
    for name, flagged in checks.items():
        count = int(flagged.sum())
        if count:
            logger.warning("%d rows: %s", count, name)


def validate(raw):
    """Split raw rows into valid rows and rejected rows with a reason."""
    reasons = find_reject_reasons(raw)
    is_rejected = reasons.notna()

    rejected = raw[is_rejected].assign(reject_reason=reasons[is_rejected])
    valid = raw[~is_rejected].copy()
    valid["Quantity"] = valid["Quantity"].astype("int64")
    valid["InvoiceDate"] = pd.to_datetime(valid["InvoiceDate"], format=TIMESTAMP_FORMAT)

    logger.info("Validation: %d valid, %d rejected", len(valid), len(rejected))
    for reason, count in rejected["reject_reason"].value_counts().items():
        logger.warning("Rejected %d rows: %s", count, reason)
    log_warnings(valid)
    return valid, rejected


def main():
    raw = read_raw_csv(COMBINED_CSV_PATH)
    validate(raw)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    main()
