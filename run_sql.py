"""
run_sql.py — executes every .sql file in sql/ against data/retail_sales.db
and prints the result of each statement. Useful for verifying the project
runs end to end, and as a stand-in for "open this in your SQL client."

Usage:
    python3 scripts/run_sql.py                 # runs every file in sql/
    python3 scripts/run_sql.py sql/02_regional_performance.sql   # runs one file
"""
import sys
import sqlite3
import glob
import re

DB_PATH = "data/retail_sales.db"


def split_statements(sql_text: str):
    # naive split on semicolons outside of strings/comments is fine here —
    # none of these scripts use semicolons inside string literals.
    stripped = re.sub(r"--.*", "", sql_text)
    return [s.strip() for s in stripped.split(";") if s.strip()]


def run_file(path: str, conn: sqlite3.Connection):
    print(f"\n{'='*78}\n{path}\n{'='*78}")
    with open(path) as f:
        sql_text = f.read()
    cur = conn.cursor()
    for stmt in split_statements(sql_text):
        cur.execute(stmt)
        if cur.description:
            cols = [d[0] for d in cur.description]
            rows = cur.fetchall()
            print(" | ".join(cols))
            for row in rows[:15]:
                print(" | ".join(str(v) for v in row))
            if len(rows) > 15:
                print(f"... ({len(rows)} rows total)")


def main():
    conn = sqlite3.connect(DB_PATH)
    files = sys.argv[1:] if len(sys.argv) > 1 else sorted(glob.glob("sql/*.sql"))
    files = [f for f in files if "00_schema" not in f]
    for f in files:
        run_file(f, conn)
    conn.close()
    print("\nAll SQL files executed with no errors.")


if __name__ == "__main__":
    main()
