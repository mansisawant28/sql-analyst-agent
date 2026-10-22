from sql_agent.tools import get_schema, run_sql


def test_schema_contains_core_tables():
    schema = get_schema()
    assert "Customer" in schema
    assert "Track" in schema

def test_run_sql_returns_expected_results():
    query = "SELECT COUNT(*) AS total FROM Track;"
    results = run_sql(query)
    assert results[0]["total"] == 3503

def test_run_sql_handles_invalid_query():
    query = "SELECT * FROM NonExistentTable;"
    results = run_sql(query)
    assert "error" in results
    assert "NonExistentTable" in results["error"]