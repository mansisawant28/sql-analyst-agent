import sqlite3
from pathlib import Path

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

def run_sql(query:str)->dict:
    conn=sqlite3.connect(DB_PATH)
    cur =conn.cursor()
    try:
        cur.execute(query)
        rows = cur.fetchall()
        columns = [col[0] for col in cur.description]
        results = [dict(zip(columns,row)) for row in rows]
    except sqlite3.Error as e:
        return {"error": str(e)}
    finally:
        conn.close()
    return results
