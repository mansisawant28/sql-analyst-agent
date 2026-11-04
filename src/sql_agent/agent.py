import json

from groq import APIStatusError

from .llm import get_llm
from .tool_specs import TOOLS
from .tools import get_schema, run_sql

SYSTEM_PROMPT = """You are a data analyst answering questions about a SQLite database.
Always call get_schema first to see the tables and columns.
Then write a SQL SELECT query and run it with run_sql.
If a query returns an error, read the message, fix the SQL and try again.
Use aliases for columns (for example Artist.Name AS artist_name).
Answer in plain English and mention the SQL you used.
Results are limited to 20 rows. If "truncated" is true, use COUNT, GROUP BY or LIMIT
to get what you need instead of reading all rows."""

MAX_STEPS = 5

TOOL_FUNCTIONS = {
    "get_schema": get_schema,
    "run_sql": run_sql,
}


def ask(question: str) -> dict:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    queries = []  # every run_sql call, with its result

    for step in range(MAX_STEPS):
        try:
            response = get_llm(messages, TOOLS)
        except APIStatusError as e:
            return {
                "answer": f"The model request failed (error {e.status_code}). Try a narrower question.",
                "queries": queries,
                "steps": step + 1,
            }

        message = response.choices[0].message

        # No tool requests means the model has given its final answer.
        if not message.tool_calls:
            return {"answer": message.content, "queries": queries, "steps": step + 1}

        # Record the model's request in the history.
        messages.append(
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                    for call in message.tool_calls
                ],
            }
        )

        # Run each requested tool and send its result back.
        for call in message.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments or "{}")
            print(f"[step {step + 1}] {name} {args}")

            if name in TOOL_FUNCTIONS:
                result = TOOL_FUNCTIONS[name](**args)
            else:
                result = {"error": f"Unknown tool: {name}"}

            if name == "run_sql":
                queries.append({"sql": args.get("query", ""), "result": result})

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result, default=str),
                }
            )

    return {
        "answer": f"I could not find an answer within {MAX_STEPS} steps.",
        "queries": queries,
        "steps": MAX_STEPS,
    }