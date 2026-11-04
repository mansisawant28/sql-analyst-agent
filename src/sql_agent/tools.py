import sqlite3
from pathlib import Path
import time

MAX_ROWS = 20
TIMEOUT_SECONDS = 5

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "chinook.db"

def get_schema()->str:
    conn=sqlite3.connect(DB_PATH)
    cur =conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    schema = {}
    for table in tables:
        table_name = table[0]
        cur.execute(f"PRAGMA table_info({table_name});")
        columns = cur.fetchall()
        schema[table_name] = [column[1] for column in columns]
    lines=[]
    for table_name,columns in schema.items():
        lines.append(f"{table_name} ({', '.join(columns)})")
        results = "\n".join(lines)
    conn.close()
    return results

def is_safe_select(query: str) -> bool:
    cleaned = query.strip().rstrip(";").strip()
    if not cleaned.lower().startswith(("select", "with")):
        return False
    if ";" in cleaned:  # more than one statement
        return False
    return True


def run_sql(query: str) -> dict:
    if not is_safe_select(query):
        return {"error": "Only a single SELECT query is allowed."}

    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    deadline = time.monotonic() + TIMEOUT_SECONDS
    conn.set_progress_handler(lambda: 1 if time.monotonic() > deadline else 0, 10000)
    cur = conn.cursor()
    try:
        cur.execute(query)
        rows = cur.fetchmany(MAX_ROWS + 1)
        truncated = len(rows) > MAX_ROWS
        rows = rows[:MAX_ROWS]
        columns = [col[0] for col in cur.description]
        results = [dict(zip(columns, row)) for row in rows]
        return {"columns": columns, "rows": results, "truncated": truncated}
    except sqlite3.Error as e:
        if "interrupted" in str(e).lower():
            return {"error": f"Query took longer than {TIMEOUT_SECONDS} seconds and was stopped."}
        return {"error": str(e)}
    finally:
        conn.close()
