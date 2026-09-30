"""
SQL Validator Module.
Ensures ONLY safe, read-only SELECT queries are executed against MySQL.
Strictly blocks destructive SQL commands, multiple statements, and injection patterns.
"""
import re
from typing import Tuple

# Blacklist of prohibited SQL commands/keywords
FORBIDDEN_KEYWORDS = [
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bDELETE\b",
    r"\bDROP\b",
    r"\bALTER\b",
    r"\bTRUNCATE\b",
    r"\bCREATE\b",
    r"\bREPLACE\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"\bEXEC\b",
    r"\bEXECUTE\b",
    r"\bMERGE\b",
    r"\bATTACH\b",
    r"\bDETACH\b",
    r"\bINTO\s+OUTFILE\b",
    r"\bINTO\s+DUMPFILE\b",
]

def clean_sql_query(raw_query: str) -> str:
    """Strips markdown formatting, leading/trailing whitespace, and trailing semicolons."""
    if not raw_query:
        return ""
    
    cleaned = raw_query.strip()
    
    # Strip markdown code block wrappers if LLM returned ```sql ... ```
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:sql)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    # Remove single-line comments (-- or #) and inline block comments (/* */)
    cleaned = re.sub(r"--[^\n]*", "", cleaned)
    cleaned = re.sub(r"#[^\n]*", "", cleaned)
    cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)

    # Trim trailing semicolon if present
    cleaned = cleaned.strip()
    if cleaned.endswith(";"):
        cleaned = cleaned[:-1].strip()

    return cleaned

def validate_sql_query(raw_query: str) -> Tuple[bool, str, str]:
    """
    Validates that a query is strictly a safe SELECT statement.
    Returns:
        (is_valid: bool, cleaned_query: str, error_message: str)
    """
    cleaned = clean_sql_query(raw_query)

    if not cleaned:
        return False, "", "Empty SQL query."

    # Prevent multiple statements separated by semicolons
    if ";" in cleaned:
        return False, cleaned, "Multiple SQL statements are not permitted."

    # Check for forbidden keywords (case-insensitive)
    for pattern in FORBIDDEN_KEYWORDS:
        if re.search(pattern, cleaned, flags=re.IGNORECASE):
            match = re.search(pattern, cleaned, flags=re.IGNORECASE).group()
            return False, cleaned, f"Destructive SQL command forbidden: '{match.upper()}'."

    # Ensure query starts strictly with SELECT or WITH (for CTEs)
    first_word_match = re.match(r"^\s*([A-Za-z]+)", cleaned)
    if not first_word_match:
        return False, cleaned, "Invalid SQL syntax: missing leading command keyword."

    first_word = first_word_match.group(1).upper()
    if first_word not in ("SELECT", "WITH"):
        return False, cleaned, f"Only read-only SELECT queries are allowed. Attempted: '{first_word}'."

    return True, cleaned, ""
