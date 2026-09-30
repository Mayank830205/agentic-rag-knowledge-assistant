"""
MySQL Database Connection and Query Execution Module.
Manages SQLAlchemy engine, schema introspection, safe query execution,
and resilient SQLite fallback when MySQL is unreachable on cloud environments.
"""
import os
import logging
from typing import List, Dict, Any, Tuple
from sqlalchemy import create_engine, text, event
from backend.config import settings
from backend.database.sql_validator import validate_sql_query

logger = logging.getLogger(__name__)

# SQLAlchemy connection engine
_engine = None
_using_sqlite_fallback = False

def _init_sqlite_fallback_data(engine):
    """Initializes and seeds SQLite fallback database if tables do not exist."""
    with engine.connect() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS departments (
            department_id INTEGER PRIMARY KEY AUTOINCREMENT,
            department_name TEXT NOT NULL UNIQUE
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department_id INTEGER NOT NULL,
            designation TEXT NOT NULL,
            salary NUMERIC NOT NULL,
            joining_date TEXT NOT NULL,
            FOREIGN KEY (department_id) REFERENCES departments(department_id)
        );
        """))
        # Check if already seeded
        count = conn.execute(text("SELECT COUNT(*) FROM departments;")).scalar()
        if count == 0:
            conn.execute(text("""
            INSERT INTO departments (department_id, department_name) VALUES
            (1, 'Engineering'),
            (2, 'Human Resources'),
            (3, 'Finance'),
            (4, 'Product Management'),
            (5, 'Sales');
            """))
            conn.execute(text("""
            INSERT INTO employees (name, department_id, designation, salary, joining_date) VALUES
            ('Alice Johnson', 1, 'Senior Software Engineer', 125000.00, '2022-03-15'),
            ('Bob Smith', 1, 'Backend Developer', 95000.00, '2023-06-01'),
            ('Charlie Davis', 1, 'DevOps Engineer', 110000.00, '2021-11-20'),
            ('Diana Miller', 1, 'Frontend Developer', 88000.00, '2024-01-10'),
            ('Ethan Wilson', 1, 'AI/ML Engineer', 135000.00, '2025-02-15'),
            ('Fiona Clark', 1, 'Software Engineer', 92000.00, '2025-04-01'),
            ('George Martin', 1, 'QA Automation Engineer', 82000.00, '2023-09-12'),
            ('Hannah White', 1, 'Engineering Manager', 155000.00, '2021-01-08'),
            ('Ian Moore', 2, 'HR Director', 120000.00, '2020-08-14'),
            ('Julia Taylor', 2, 'Talent Acquisition Specialist', 70000.00, '2023-02-18'),
            ('Kevin Anderson', 2, 'HR Generalist', 65000.00, '2024-07-01'),
            ('Laura Thomas', 2, 'People Operations Lead', 85000.00, '2022-10-11'),
            ('Michael Jackson', 3, 'Chief Financial Officer', 175000.00, '2019-05-01'),
            ('Nora Harris', 3, 'Senior Financial Analyst', 98000.00, '2022-04-19'),
            ('Oliver Lewis', 3, 'Accountant', 72000.00, '2023-11-05'),
            ('Penelope Young', 3, 'Payroll Specialist', 68000.00, '2025-01-20'),
            ('Quinn Hall', 4, 'VP of Product', 165000.00, '2020-03-10'),
            ('Rachel Allen', 4, 'Senior Product Manager', 130000.00, '2022-09-01'),
            ('Samuel King', 4, 'Product Designer', 90000.00, '2023-04-15'),
            ('Tina Scott', 4, 'Associate Product Manager', 78000.00, '2025-03-01'),
            ('Uma Green', 5, 'Sales Director', 140000.00, '2021-06-15'),
            ('Victor Baker', 5, 'Enterprise Account Executive', 105000.00, '2022-12-01'),
            ('Wendy Adams', 5, 'Business Development Rep', 62000.00, '2024-05-10'),
            ('Xavier Nelson', 5, 'Customer Success Manager', 80000.00, '2023-08-22'),
            ('Yvonne Carter', 5, 'Sales Operations Analyst', 75000.00, '2025-05-18');
            """))
            conn.commit()

def get_engine():
    """
    Returns a singleton SQLAlchemy engine.
    Tries MySQL first; if unreachable, falls back to local SQLite with identical schema & data.
    """
    global _engine, _using_sqlite_fallback
    if _engine is None:
        mysql_url = settings.get_mysql_connection_url()
        try:
            test_engine = create_engine(
                mysql_url,
                pool_pre_ping=True,
                pool_recycle=3600,
                pool_size=5,
                max_overflow=10,
                connect_args={"connect_timeout": 3}
            )
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            _engine = test_engine
            _using_sqlite_fallback = False
            logger.info("Successfully connected to MySQL database.")
        except Exception as e:
            logger.warning(f"MySQL connection failed ({e}). Falling back to SQLite for cloud/standalone resilience.")
            os.makedirs("data", exist_ok=True)
            sqlite_path = os.path.abspath(os.path.join("data", "agentrag_fallback.db")).replace("\\", "/")
            sqlite_url = f"sqlite:///{sqlite_path}"
            _engine = create_engine(
                sqlite_url,
                connect_args={"check_same_thread": False}
            )
            @event.listens_for(_engine, "connect")
            def setup_sqlite_functions(dbapi_connection, connection_record):
                # Register MySQL YEAR() function in SQLite
                dbapi_connection.create_function(
                    "YEAR", 1,
                    lambda d: int(str(d)[:4]) if d and len(str(d)) >= 4 else None
                )

            _init_sqlite_fallback_data(_engine)
            _using_sqlite_fallback = True

    return _engine

def check_database_connection() -> Tuple[bool, str]:
    """Tests if MySQL database is reachable, or reports operational SQLite fallback."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            if result == 1:
                db_name = "SQLite Fallback (Cloud Mode)" if _using_sqlite_fallback else "MySQL (Production Mode)"
                return True, f"{db_name} operational."
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
    Validates and executes a SELECT query safely against MySQL (or SQLite fallback).
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
