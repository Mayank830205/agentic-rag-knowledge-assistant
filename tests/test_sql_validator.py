"""
Tests for SQL Validation and Security Guardrails.
Verifies that only safe, read-only SELECT queries are allowed, and all destructive operations are blocked.
"""
import pytest
from backend.database.sql_validator import validate_sql_query, clean_sql_query

def test_clean_sql_query_removes_markdown():
    raw = "```sql\nSELECT * FROM employees;\n```"
    cleaned = clean_sql_query(raw)
    assert cleaned == "SELECT * FROM employees"

def test_clean_sql_query_removes_comments():
    raw = "SELECT * FROM employees -- fetch all employees\nWHERE salary > 50000"
    cleaned = clean_sql_query(raw)
    assert "--" not in cleaned
    assert "salary > 50000" in cleaned

def test_valid_select_queries_pass():
    valid_queries = [
        "SELECT * FROM employees",
        "SELECT COUNT(*) FROM departments",
        "SELECT name, salary FROM employees WHERE salary > 100000 ORDER BY salary DESC",
        "SELECT d.department_name, AVG(e.salary) FROM employees e JOIN departments d ON e.department_id = d.department_id GROUP BY d.department_name",
        "WITH high_earners AS (SELECT * FROM employees WHERE salary > 120000) SELECT * FROM high_earners"
    ]
    for q in valid_queries:
        is_valid, cleaned, err = validate_sql_query(q)
        assert is_valid is True, f"Failed on valid query: {q}, err: {err}"
        assert err == ""

def test_destructive_queries_are_rejected():
    destructive_queries = [
        ("DROP TABLE employees", "DROP"),
        ("DELETE FROM employees WHERE employee_id = 1", "DELETE"),
        ("TRUNCATE TABLE departments", "TRUNCATE"),
        ("INSERT INTO departments (department_name) VALUES ('Hacking')", "INSERT"),
        ("UPDATE employees SET salary = 999999 WHERE employee_id = 1", "UPDATE"),
        ("ALTER TABLE employees ADD COLUMN ssn VARCHAR(20)", "ALTER"),
        ("CREATE TABLE malicious (id INT)", "CREATE"),
        ("GRANT ALL PRIVILEGES ON *.* TO 'attacker'@'%'", "GRANT"),
    ]
    for query, keyword in destructive_queries:
        is_valid, cleaned, err = validate_sql_query(query)
        assert is_valid is False, f"Destructive query should be rejected: {query}"
        assert "forbidden" in err.lower() or "only read-only select" in err.lower()

def test_multiple_statements_injection_rejected():
    injection_queries = [
        "SELECT * FROM employees; DROP TABLE employees",
        "SELECT * FROM departments; INSERT INTO departments VALUES (99, 'Evil')",
        "SELECT 1; SELECT 2"
    ]
    for q in injection_queries:
        is_valid, cleaned, err = validate_sql_query(q)
        assert is_valid is False, f"Chained statement should be rejected: {q}"
        assert "multiple sql statements" in err.lower()

def test_empty_query_rejected():
    is_valid, cleaned, err = validate_sql_query("   ")
    assert is_valid is False
    assert "empty" in err.lower()
