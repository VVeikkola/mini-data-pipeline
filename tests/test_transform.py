import pandas as pd

from transform import apply_fixes, build_tables, classify_rows


def make_valid_rows(rows):
    """Rows as they look after validation."""
    df = pd.DataFrame(rows)
    df["Quantity"] = df["Quantity"].astype("int64")
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    return df


def row(
    invoice,
    stock_code,
    quantity=1,
    price="1.00",
    description="ITEM",
    customer="13085.0",
    when="2010-01-01 10:00:00",
):
    return {
        "Invoice": invoice,
        "StockCode": stock_code,
        "Description": description,
        "Quantity": quantity,
        "InvoiceDate": when,
        "Price": price,
        "Customer ID": customer,
        "Country": "United Kingdom",
    }


def test_apply_fixes():
    df = make_valid_rows([row("1", " 15056bl ", description=" PARASOL ")])
    fixed = apply_fixes(df)
    assert fixed.loc[0, "StockCode"] == "15056BL"
    assert fixed.loc[0, "Description"] == "PARASOL"
    assert fixed.loc[0, "Customer ID"] == "13085"


def test_classify_rows_first_matching_rule_wins():
    df = make_valid_rows(
        [
            row("489434", "85048"),  # sale
            row("C489449", "85048", quantity=-1),  # cancellation
            row("C489450", "POST", quantity=-1),  # cancelled postage
            row("489500", "20713", quantity=-5, price="0"),  # stock adjustment
            row("A506401", "B", price="-53594.36"),  # bad debt
            row("489501", "GIFT_0001_20"),  # gift voucher
        ]
    )
    assert list(classify_rows(df)) == [
        "sale",
        "cancellation",
        "non_product",
        "stock_adjustment",
        "accounting_adjustment",
        "non_product",
    ]


def test_build_tables():
    df = make_valid_rows(
        [
            row("1", "A", description="RED MUG", when="2010-01-01 10:01:00"),
            row("1", "A", description="RED MUG", when="2010-01-01 10:00:00"),
            row("2", "B", description="CUP BLUE", customer=None),
            row("2", "B", description="BLUE CUP", customer=None),
            row("3", "C", description=None),
        ]
    )
    df["row_type"] = "sale"

    tables = build_tables(apply_fixes(df))

    products = tables["products"].set_index("stock_code")["description"]
    assert products["A"] == "RED MUG"
    assert products["B"] == "BLUE CUP"  # tie broken alphabetically
    assert pd.isna(products["C"])  # product without description is kept

    invoices = tables["invoices"].set_index("invoice_no")
    assert invoices.loc["1", "invoiced_at"] == pd.Timestamp("2010-01-01 10:00:00")
    assert pd.isna(invoices.loc["2", "customer_id"])

    assert list(tables["customers"]["customer_id"]) == ["13085"]
    assert len(tables["invoice_lines"]) == 5
