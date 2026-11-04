from sql_agent.tools import get_schema, is_safe_select, run_sql


def test_schema_contains_core_tables():
    schema = get_schema()
    assert "Customer" in schema
    assert "Track" in schema

def test_run_sql_returns_expected_results():
    query = "SELECT COUNT(*) AS total FROM Track;"
    results = run_sql(query)
    assert results["rows"][0]["total"] == 3503

def test_run_sql_handles_invalid_query():
    query = "SELECT * FROM NonExistentTable;"
    results = run_sql(query)
    assert "error" in results
    assert "NonExistentTable" in results["error"]

def test_run_sql_cannot_modify_data():
    result = run_sql("DELETE FROM Track")
    assert "error" in result

    count = run_sql("SELECT COUNT(*) AS total FROM Track")
    assert count["rows"][0]["total"] == 3503

def test_rejects_non_select():
    result = run_sql("DROP TABLE Track")
    assert "error" in result
    assert "SELECT" in result["error"]


def test_rejects_multiple_statements():
    result = run_sql("SELECT 1; DROP TABLE Track")
    assert "error" in result


def test_lowercase_select_works():
    result = run_sql("select count(*) as total from Track")
    assert result["rows"][0]["total"] == 3503


def test_with_query_works():
    result = run_sql("WITH t AS (SELECT 1 AS x) SELECT x FROM t")
    assert result["rows"][0]["x"] == 1


def test_whitespace_and_trailing_semicolon_work():
    result = run_sql("   SELECT COUNT(*) AS total FROM Track;  ")
    assert result["rows"][0]["total"] == 3503


def test_is_safe_select_helper():
    assert is_safe_select("SELECT 1")
    assert not is_safe_select("DELETE FROM Track")

def test_row_limit_truncates_large_results():
    result = run_sql("SELECT * FROM Track")
    assert len(result["rows"]) == 100
    assert result["truncated"] is True


def test_small_results_not_truncated():
    result = run_sql("SELECT * FROM Genre")
    assert result["truncated"] is False


def test_slow_query_is_stopped():
    slow = """
    WITH RECURSIVE r(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM r)
    SELECT COUNT(*) FROM r
    """
    result = run_sql(slow)
    assert "error" in result