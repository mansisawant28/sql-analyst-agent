import json

from .llm import get_llm
from .tool_specs import TOOLS
from .tools import get_schema, run_sql

SYSTEM_PROMPT = """You are a data analyst answering questions about a SQLite database.
Always call get_schema first to see the tables and columns.
Then write a SQL SELECT query and run it with run_sql.
If a query returns an error, read the message, fix the SQL and try again.
Use aliases for columns (for example Artist.Name AS artist_name).
Answer in plain English and mention the SQL you used."""

MAX_STEPS = 5

TOOL_FUNCTIONS = {
    "get_schema": get_schema,
    "run_sql": run_sql,
}


def ask(question: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    for step in range(MAX_STEPS):
        response = get_llm(messages, TOOLS)
        message = response.choices[0].message

        # No tool requests means the model has given its final answer.
        if not message.tool_calls:
            return message.content

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

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result, default=str),
                }
            )

    return f"I could not find an answer within {MAX_STEPS} steps."