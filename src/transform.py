import logging

import numpy as np
import pandas as pd

from config import COMBINED_CSV_PATH
from ingest import read_raw_csv
from validate import validate

logger = logging.getLogger(__name__)

NON_PRODUCT_CODES = {
    "POST",
    "DOT",
    "C2",
    "C3",
    "M",
    "D",
    "S",
    "B",  # manual entry, discount, samples, bad debt
    "ADJUST",
    "ADJUST2",  # manual adjustments
    "BANK CHARGES",
    "AMAZONFEE",
    "CRUK",
    "TEST001",
    "TEST002",  # test products
    "GIFT",
}
GIFT_VOUCHER_PREFIX = "GIFT_"


def apply_fixes(df):
    """Apply the FIX rules from the data contract."""
    fixed = df.copy()
    fixed["StockCode"] = fixed["StockCode"].str.strip().str.upper()
    fixed["Description"] = fixed["Description"].str.strip().replace("", pd.NA)
    fixed["Customer ID"] = fixed["Customer ID"].str.replace(r"\.0$", "", regex=True)
    return fixed


def classify_rows(df):
    """Return the row_type for each row. The first matching rule wins."""
    is_non_product = df["StockCode"].isin(NON_PRODUCT_CODES) | df[
        "StockCode"
    ].str.startswith(GIFT_VOUCHER_PREFIX)
    price = pd.to_numeric(df["Price"])
    conditions = [
        df["Invoice"].str.startswith("A"),
        is_non_product,
        df["Invoice"].str.startswith("C"),
        (df["Quantity"] < 0) & (price == 0),
    ]
    choices = [
        "accounting_adjustment",
        "non_product",
        "cancellation",
        "stock_adjustment",
    ]
    return pd.Series(np.select(conditions, choices, default="sale"), index=df.index)


def build_tables(df):
    """Split flat rows into the four tables of the data model."""
    customers = (
        df[["Customer ID"]]
        .dropna()
        .drop_duplicates()
        .rename(columns={"Customer ID": "customer_id"})
        .sort_values("customer_id")
    )

    most_frequent_names = (
        df.dropna(subset=["Description"])
        .groupby(["StockCode", "Description"])
        .size()
        .reset_index(name="n")
        .sort_values(["StockCode", "n", "Description"], ascending=[True, False, True])
        .drop_duplicates("StockCode")
    )
    products = (
        df[["StockCode"]]
        .drop_duplicates()
        .merge(
            most_frequent_names[["StockCode", "Description"]],
            on="StockCode",
            how="left",
        )
        .rename(columns={"StockCode": "stock_code", "Description": "description"})
        .sort_values("stock_code")
    )

    invoices = (
        df.groupby("Invoice")
        .agg(
            customer_id=("Customer ID", "first"),
            invoiced_at=("InvoiceDate", "min"),
            country=("Country", "first"),
        )
        .reset_index()
        .rename(columns={"Invoice": "invoice_no"})
    )

    invoice_lines = df.rename(
        columns={
            "Invoice": "invoice_no",
            "StockCode": "stock_code",
            "Quantity": "quantity",
            "Price": "unit_price",
        }
    )[["invoice_no", "stock_code", "quantity", "unit_price", "row_type"]]

    return {
        "customers": customers,
        "products": products,
        "invoices": invoices,
        "invoice_lines": invoice_lines,
    }


def transform(valid):
    """Turn validated rows into tables ready for loading."""
    df = apply_fixes(valid)
    df["row_type"] = classify_rows(df)
    tables = build_tables(df)

    for name, table in tables.items():
        logger.info("Table %s: %d rows", name, len(table))
    for row_type, count in df["row_type"].value_counts().items():
        logger.info("row_type %s: %d rows", row_type, count)
    return tables


def main():
    valid, _ = validate(read_raw_csv(COMBINED_CSV_PATH))
    transform(valid)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    main()
