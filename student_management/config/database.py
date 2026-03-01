"""
database.py — Database configuration and connection management
Supports both mysql-connector-python and PyMySQL as the driver.
"""

import os
import sys
import logging
from contextlib import contextmanager
from typing import Optional

# ---------------------------------------------------------------------------
# Try mysql-connector-python first, fall back to PyMySQL
# ---------------------------------------------------------------------------
try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    DRIVER = "mysql-connector"
except ImportError:
    try:
        import pymysql
        import pymysql.cursors
        MySQLError = pymysql.MySQLError
        DRIVER = "pymysql"
    except ImportError:
        sys.exit(
            "[DB] Neither mysql-connector-python nor PyMySQL is installed.\n"
            "Run:  pip install mysql-connector-python"
        )

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration — override with environment variables for production
# ---------------------------------------------------------------------------
DB_CONFIG: dict = {
    "host":     os.getenv("DB_HOST",     "localhost"),
    "port":     int(os.getenv("DB_PORT", "3306")),
    "database": os.getenv("DB_NAME",     "student_management_db"),
    "user":     os.getenv("DB_USER",     "root"),
    "password": os.getenv("DB_PASSWORD", "12345"),
    "charset":  "utf8mb4",
}


# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------
def get_connection():
    """Return a new database connection.  Caller is responsible for closing."""
    try:
        if DRIVER == "mysql-connector":
            conn = mysql.connector.connect(**DB_CONFIG)
        else:
            cfg = {k: v for k, v in DB_CONFIG.items() if k != "charset"}
            conn = pymysql.connect(
                cursorclass=pymysql.cursors.DictCursor,
                charset="utf8mb4",
                **cfg,
            )
        logger.debug("[DB] Connection established via %s", DRIVER)
        return conn
    except MySQLError as exc:
        logger.error("[DB] Connection failed: %s", exc)
        raise


@contextmanager
def db_session(dictionary: bool = True):
    """Context manager that provides a cursor and auto-commits / rolls back.

    Usage::

        with db_session() as cursor:
            cursor.execute("SELECT ...")
            rows = cursor.fetchall()
    """
    conn = get_connection()
    try:
        if DRIVER == "mysql-connector":
            cursor = conn.cursor(dictionary=dictionary)
        else:
            cursor = conn.cursor()          # PyMySQL always returns dicts here
        yield cursor
        conn.commit()
    except MySQLError as exc:
        conn.rollback()
        logger.error("[DB] Transaction rolled back: %s", exc)
        raise
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------
def test_connection() -> bool:
    """Ping the database and return True on success."""
    try:
        with db_session() as cur:
            cur.execute("SELECT 1 AS ping")
            row = cur.fetchone()
            ok = (row.get("ping") if isinstance(row, dict) else row[0]) == 1
        if ok:
            logger.info("[DB] Connection test PASSED  (driver: %s, db: %s)",
                        DRIVER, DB_CONFIG["database"])
        return ok
    except Exception as exc:          # noqa: BLE001
        logger.error("[DB] Connection test FAILED: %s", exc)
        return False


def execute_query(sql: str, params: Optional[tuple] = None) -> list[dict]:
    """Execute a SELECT query and return all rows as a list of dicts."""
    with db_session() as cur:
        cur.execute(sql, params or ())
        return cur.fetchall() or []


def execute_non_query(sql: str, params: Optional[tuple] = None) -> int:
    """Execute INSERT/UPDATE/DELETE and return affected row count."""
    with db_session() as cur:
        cur.execute(sql, params or ())
        return cur.rowcount


def call_procedure(proc_name: str, args: tuple = ()) -> list:
    """Call a stored procedure and return all result sets."""
    results = []
    with db_session() as cur:
        cur.callproc(proc_name, args)
        for result in cur.stored_results():
            results.append(result.fetchall())
    return results


# ---------------------------------------------------------------------------
# Quick test when run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
    if test_connection():
        rows = execute_query("SELECT dept_code, dept_name FROM departments LIMIT 5")
        print("\nDepartments in database:")
        for r in rows:
            print(f"  {r['dept_code']:6s}  {r['dept_name']}")
    else:
        print("Could not connect. Check DB_USER / DB_PASSWORD environment variables.")
