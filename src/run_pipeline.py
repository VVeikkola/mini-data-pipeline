import logging

import extract
from config import COMBINED_CSV_PATH
from db import get_connection
from ingest import read_raw_csv
from load import load
from transform import transform
from validate import validate

logger = logging.getLogger(__name__)


def start_run():
    """Insert a 'running' row and return its run_id."""
    with get_connection() as conn:
        row = conn.execute(
            "INSERT INTO pipeline_runs (status) VALUES ('running') RETURNING run_id"
        ).fetchone()
    return row[0]


def finish_run(run_id, status, stats, error=None):
    """Store the final status and row counts of a run."""
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE pipeline_runs
            SET finished_at = now(), status = %s, source_sha256 = %s,
                rows_read = %s, rows_valid = %s, rows_rejected = %s,
                rows_loaded = %s, error_message = %s
            WHERE run_id = %s
            """,
            (
                status,
                stats.get("source_sha256"),
                stats.get("rows_read"),
                stats.get("rows_valid"),
                stats.get("rows_rejected"),
                stats.get("rows_loaded"),
                error,
                run_id,
            ),
        )


def count_loaded_lines():
    """Count lines actually stored in the database."""
    with get_connection() as conn:
        return conn.execute("SELECT count(*) FROM invoice_lines").fetchone()[0]


def run():
    if not COMBINED_CSV_PATH.exists():
        logger.info("Combined CSV not found, running extract first")
        extract.main()

    run_id = start_run()
    logger.info("Pipeline run %d started", run_id)
    stats = {}
    try:
        stats["source_sha256"] = extract.compute_sha256(COMBINED_CSV_PATH)
        raw = read_raw_csv(COMBINED_CSV_PATH)
        valid, rejected = validate(raw)
        stats.update(
            rows_read=len(raw), rows_valid=len(valid), rows_rejected=len(rejected)
        )

        if stats["rows_read"] != stats["rows_valid"] + stats["rows_rejected"]:
            raise ValueError(f"Validation lost rows: {stats}")

        load(transform(valid), rejected)
        stats["rows_loaded"] = count_loaded_lines()

        if stats["rows_loaded"] != stats["rows_valid"]:
            raise ValueError(
                f"Loaded {stats['rows_loaded']} lines, expected {stats['rows_valid']}"
            )
    except Exception as exc:
        finish_run(run_id, "failed", stats, error=str(exc))
        logger.exception("Pipeline run %d failed", run_id)
        raise

    finish_run(run_id, "success", stats)
    logger.info(
        "Pipeline run %d succeeded: %d read, %d valid, %d rejected, %d loaded",
        run_id,
        stats["rows_read"],
        stats["rows_valid"],
        stats["rows_rejected"],
        stats["rows_loaded"],
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    run()
