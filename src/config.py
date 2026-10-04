import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

DATA_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data"))
SOURCE_PATH = DATA_DIR / "online_retail_II.xlsx"
COMBINED_CSV_PATH = DATA_DIR / "combined_retail_data.csv"

DB_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DB_NAME = os.environ["POSTGRES_DB"]
DB_USER = os.environ["POSTGRES_USER"]
DB_PASSWORD = os.environ["POSTGRES_PASSWORD"]
