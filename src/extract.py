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


def main():
    verify_checksum(SOURCE_PATH, EXPECTED_SHA256)
    print(f"Checksum verified for {SOURCE_PATH}. Proceeding to read sheets.")

    sheets = read_sheets(SOURCE_PATH)
    for sheet_name, df in sheets.items():
        print(f"Sheet: {sheet_name}, Rows: {len(df)}, Columns: {len(df.columns)}")


if __name__ == "__main__":
    main()
