import pandas as pd
import pytest

from validate import validate

VALID_ROW = {
    "Invoice": "489434",
    "StockCode": "85048",
    "Description": "15CM CHRISTMAS GLASS BALL 20 LIGHTS",
    "Quantity": "12",
    "InvoiceDate": "2009-12-01 07:45:00",
    "Price": "6.95",
    "Customer ID": "13085.0",
    "Country": "United Kingdom",
}


def make_rows(*changes):
    """Build a DataFrame where each row is VALID_ROW with some fields changed."""
    return pd.DataFrame([{**VALID_ROW, **change} for change in changes], dtype="str")


@pytest.mark.parametrize(
    "change, expected_reason",
    [
        ({"Invoice": "X1"}, "invalid_invoice"),
        ({"Invoice": None}, "invalid_invoice"),
        ({"StockCode": None}, "missing_stock_code"),
        ({"Quantity": "0"}, "invalid_quantity"),
        ({"Quantity": "abc"}, "invalid_quantity"),
        ({"Quantity": "2.5"}, "invalid_quantity"),
        ({"InvoiceDate": "2009-13-01 07:45:00"}, "invalid_invoice_date"),
        ({"Price": "-1"}, "invalid_price"),
        ({"Price": "abc"}, "invalid_price"),
    ],
)
def test_invalid_rows_are_rejected_with_reason(change, expected_reason):
    valid, rejected = validate(make_rows(change))
    assert valid.empty
    assert list(rejected["reject_reason"]) == [expected_reason]


@pytest.mark.parametrize(
    "change",
    [
        {},
        {"Invoice": "C489449", "Quantity": "-1"},  # cancellation
        {"Invoice": "A506401", "Price": "-53594.36"},  # bad debt adjustment
        {"Customer ID": None},  # unknown customer
        {"Price": "0"},  # zero price is allowed
    ],
)
def test_valid_edge_cases_are_kept(change):
    valid, rejected = validate(make_rows(change))
    assert len(valid) == 1
    assert rejected.empty


def test_valid_rows_get_proper_types_and_keep_price_as_text():
    valid, _ = validate(make_rows({}))
    assert valid["Quantity"].dtype == "int64"
    assert str(valid["InvoiceDate"].dtype).startswith("datetime64")
    assert valid.iloc[0]["Price"] == "6.95"
