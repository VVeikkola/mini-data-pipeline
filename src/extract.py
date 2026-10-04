import hashlib
import logging

import pandas as pd

from config import COMBINED_CSV_PATH, SOURCE_PATH

logger = logging.getLogger(__name__)

EXPECTED_SHA256 = "bcbe73b35f5b7babf197fb0cb983a11f5d9ff929078d4aa53d171b1f2df2e980"
CHUNK_SIZE = 8192


def compute_sha256(path):
    """Return the SHA256 hex digest of the file at path."""
    h = hashlib.sha256()
    with open(path, "rb") as file:
        while chunk := file.read(CHUNK_SIZE):
            h.update(chunk)
    return h.hexdigest()


def verify_checksum(path, expected):
    """Stop with a clear error if the file checksum does not match."""
    computed = compute_sha256(path)
    if computed != expected:
        raise ValueError(
            f"Checksum mismatch for {path}: expected {expected}, got {computed}"
        )


def read_sheets(path):
    """Read all sheets from the Excel file."""
    with pd.ExcelFile(path) as xls:
        sheets = {}
        for sheet_name in xls.sheet_names:
            sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
    return sheets


def combine_sheets(sheets):
    """
    Combine workbook sheets into one DataFrame
    while removing the duplicated overlap period.
    """
    sheet1 = sheets["Year 2009-2010"]
    sheet2 = sheets["Year 2010-2011"]

    overlap_start = pd.Timestamp("2010-12-01")
    overlap_end = pd.Timestamp("2010-12-10")

    in_overlap_1 = (sheet1["InvoiceDate"] >= overlap_start) & (
        sheet1["InvoiceDate"] < overlap_end
    )
    in_overlap_2 = (sheet2["InvoiceDate"] >= overlap_start) & (
        sheet2["InvoiceDate"] < overlap_end
    )

    if in_overlap_1.sum() != in_overlap_2.sum():
        raise ValueError(
            f"Overlap mismatch: sheet1 has {in_overlap_1.sum()} rows, "
            f"sheet2 has {in_overlap_2.sum()} rows in the overlap period"
        )

    sheet2_without_overlap = sheet2[~in_overlap_2]
    return pd.concat([sheet1, sheet2_without_overlap], ignore_index=True)


def write_csv(df, path):
    """Write the DataFrame to a CSV file."""

    df.to_csv(path, index=False, encoding="utf-8", lineterminator="\n")


def main():
    verify_checksum(SOURCE_PATH, EXPECTED_SHA256)
    logger.info("Checksum verified for %s. Proceeding to read sheets.", SOURCE_PATH)

    sheets = read_sheets(SOURCE_PATH)
    for sheet_name, df in sheets.items():
        logger.info(
            "Sheet: %s, Rows: %d, Columns: %d", sheet_name, len(df), len(df.columns)
        )

    combined_df = combine_sheets(sheets)
    logger.info(
        "Combined DataFrame: %d rows, %d columns",
        len(combined_df),
        len(combined_df.columns),
    )

    total_rows = sum(len(df) for df in sheets.values())
    logger.info("Removed overlap rows: %d", total_rows - len(combined_df))

    write_csv(combined_df, COMBINED_CSV_PATH)
    output_checksum = compute_sha256(COMBINED_CSV_PATH)
    logger.info("Combined data written to %s", COMBINED_CSV_PATH)
    logger.info("Output file checksum: %s", output_checksum)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    main()
