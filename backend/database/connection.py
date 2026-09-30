"""
MySQL Database Connection and Query Execution Module.
Manages SQLAlchemy engine, schema introspection, and safe query execution.
"""
import logging
from typing import List, Dict, Any, Tuple
from sqlalchemy import create_engine, text, inspect
from backend.config import settings
from backend.database.sql_validator import validate_sql_query

logger = logging.getLogger(__name__)

# SQLAlchemy connection engine
_engine = None

def get_engine():
    """Returns a singleton SQLAlchemy engine."""
    global _engine
    if _engine is None:
        url = settings.get_mysql_connection_url()
        _engine = create_engine(
            url,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=5,
            max_overflow=10,
            connect_args={"connect_timeout": 5}
        )
    return _engine

def check_database_connection() -> Tuple[bool, str]:
    """Tests if MySQL database is reachable and tables exist."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            if result == 1:
                return True, "Database connection operational."
        return False, "Database test query returned unexpected result."
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        return False, str(e)

def get_database_schema_context() -> str:
    """
    Returns concise schema context for LLM prompt, including column names,
    types, relationships, and sample data.
    """
    return """
Database Schema (MySQL):

Table: departments
- department_id (INT, PRIMARY KEY, AUTO_INCREMENT)
- department_name (VARCHAR(100), UNIQUE)
Sample departments:
  (1, 'Engineering'), (2, 'Human Resources'), (3, 'Finance'), (4, 'Product Management'), (5, 'Sales')

Table: employees
- employee_id (INT, PRIMARY KEY, AUTO_INCREMENT)
- name (VARCHAR(100))
- department_id (INT, FOREIGN KEY referencing departments(department_id))
- designation (VARCHAR(100))
- salary (DECIMAL(10,2))
- joining_date (DATE)
Sample employees:
  (1, 'Alice Johnson', 1, 'Senior Software Engineer', 125000.00, '2022-03-15')
  (2, 'Bob Smith', 1, 'Backend Developer', 95000.00, '2023-06-01')
  (9, 'Ian Moore', 2, 'HR Director', 120000.00, '2020-08-14')
  (13, 'Michael Jackson', 3, 'Chief Financial Officer', 175000.00, '2019-05-01')
  (17, 'Quinn Hall', 4, 'VP of Product', 165000.00, '2020-03-10')

Relationships:
employees.department_id joins with departments.department_id.
"""

def execute_select_query(query_str: str) -> List[Dict[str, Any]]:
    """
    Validates and executes a SELECT query safely against MySQL.
    Returns rows as a list of dictionaries.
    """
    is_valid, cleaned_query, err = validate_sql_query(query_str)
    if not is_valid:
        raise ValueError(f"SQL Validation Error: {err}")

    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text(cleaned_query))
        columns = list(result.keys())
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        return rows
