import os

# Integration tests use their own database, never the development data.
os.environ["POSTGRES_DB"] = "retail_test"
