import hashlib
import pandas as pd

SOURCE_PATH = "data/online_retail_II.xlsx"
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


def main():
    verify_checksum(SOURCE_PATH, EXPECTED_SHA256)
    print(f"Checksum verified for {SOURCE_PATH}. Proceeding to read sheets.")

    sheets = read_sheets(SOURCE_PATH)
    for sheet_name, df in sheets.items():
        print(f"Sheet: {sheet_name}, Rows: {len(df)}, Columns: {len(df.columns)}")

    combined_df = combine_sheets(sheets)
    print(
        f"Combined DataFrame: {len(combined_df)} rows, {len(combined_df.columns)} columns"
    )

    total_rows = sum(len(df) for df in sheets.values())
    print(f"Removed overlap rows: {total_rows - len(combined_df)}")


if __name__ == "__main__":
    main()
