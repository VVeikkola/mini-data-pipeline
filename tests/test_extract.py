import pandas as pd
import pytest

from extract import combine_sheets, compute_sha256, verify_checksum

HELLO_SHA256 = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_compute_sha256_matches_known_value(tmp_path):
    file = tmp_path / "hello.txt"
    file.write_bytes(b"hello")
    assert compute_sha256(file) == HELLO_SHA256


def test_verify_checksum_raises_on_mismatch(tmp_path):
    file = tmp_path / "hello.txt"
    file.write_bytes(b"hello")
    with pytest.raises(ValueError, match="Checksum mismatch"):
        verify_checksum(file, "0" * 64)


def make_sheet(dates, invoices):
    return pd.DataFrame({"Invoice": invoices, "InvoiceDate": pd.to_datetime(dates)})


def test_combine_sheets_removes_overlap_but_keeps_real_duplicates():
    sheet1 = make_sheet(
        ["2010-11-30 10:00", "2010-11-30 10:00", "2010-12-05 10:00"],
        ["1", "1", "2"],  # the first two rows are a genuine exact duplicate
    )
    sheet2 = make_sheet(["2010-12-05 10:00", "2010-12-15 10:00"], ["2", "3"])

    combined = combine_sheets({"Year 2009-2010": sheet1, "Year 2010-2011": sheet2})

    assert list(combined["Invoice"]) == ["1", "1", "2", "3"]


def test_combine_sheets_fails_when_overlap_counts_differ():
    sheet1 = make_sheet(["2010-12-05 10:00"], ["2"])
    sheet2 = make_sheet(["2010-12-05 10:00", "2010-12-06 10:00"], ["2", "4"])

    with pytest.raises(ValueError, match="Overlap mismatch"):
        combine_sheets({"Year 2009-2010": sheet1, "Year 2010-2011": sheet2})
