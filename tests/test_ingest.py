import pytest

from ingest import EXPECTED_COLUMNS, read_raw_csv

HEADER = ",".join(EXPECTED_COLUMNS)


def test_text_like_na_is_not_treated_as_missing(tmp_path):
    file = tmp_path / "data.csv"
    file.write_text(HEADER + "\n489434,85048,NULL,1,2009-12-01 07:45:00,1.0,,NA\n")

    df = read_raw_csv(file)

    assert df.loc[0, "Description"] == "NULL"
    assert df.loc[0, "Country"] == "NA"
    assert df["Customer ID"].isna().all()


def test_unexpected_columns_stop_the_run(tmp_path):
    file = tmp_path / "data.csv"
    file.write_text("Invoice,Wrong\n1,2\n")
    with pytest.raises(ValueError, match="Unexpected columns"):
        read_raw_csv(file)


def test_empty_file_stops_the_run(tmp_path):
    file = tmp_path / "data.csv"
    file.write_text(HEADER + "\n")
    with pytest.raises(ValueError, match="No rows"):
        read_raw_csv(file)
