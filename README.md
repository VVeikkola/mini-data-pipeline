# Mini Data Pipeline

A Python pipeline that loads sales data from online_retail_II.xlsx into a PostgreSQL database.

The source data has real quality issues, such as overlapping date ranges between source sheets and missing Customer ID, so the pipeline validates and cleans the data before loading it.

**Status:** Work in progress. See [data contract](docs/data_contract.md).