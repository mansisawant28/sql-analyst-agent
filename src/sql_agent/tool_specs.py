run_sql_spec = {
    "type": "function",
    "function": {
        "name": "run_sql",
        "description": "Run a read-only SQL query against the Chinook SQLite database and return the rows, or an error message if the query fails.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The SQL SELECT query to run.",
                }
            },
            "required": ["query"],
        },
    },
}

get_schema_spec = {
    "type": "function",
    "function": {
        "name": "get_schema",
        "description": "Get the schema of the Chinook SQLite database, including table names and their columns.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}

TOOLS = [get_schema_spec, run_sql_spec]