"""
SQL Generation and Execution Node.
Converts natural language queries into safe SELECT queries, validates against destructive operations,
executes against MySQL, and synthesizes grounded answers.
"""
import logging
from typing import Tuple, List, Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config import settings
from backend.database.connection import get_database_schema_context, execute_select_query
from backend.database.sql_validator import validate_sql_query, clean_sql_query

logger = logging.getLogger(__name__)

SQL_GENERATION_PROMPT = """You are a senior MySQL database expert.
Given the database schema below, translate the user's question into a clean, safe, and syntactically correct MySQL SELECT query.

{schema_context}

RULES:
1. Return ONLY the raw SQL query. Do NOT include markdown code blocks, explanations, comments, or backticks.
2. ONLY generate SELECT queries. NEVER write INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, or CREATE statements.
3. For aggregations like average salary, use ROUND(AVG(salary), 2).
4. For year comparisons, use YEAR(joining_date) = YYYY.
5. Department matching should handle case sensitivity gracefully (e.g. LOWER(d.department_name) = LOWER('Engineering')).
6. For listing queries, always select relevant columns like name, designation, salary, department_name.

Question: {question}
SQL Query:"""

SQL_SYNTHESIS_PROMPT = """You are an enterprise data assistant.
Provide a clear, concise, and professional natural language answer to the user's question using ONLY the provided SQL query and database results.

Question: {question}
Executed SQL: {sql_query}
Database Results: {sql_results}

Answer:"""

sql_gen_prompt = PromptTemplate(
    template=SQL_GENERATION_PROMPT,
    input_variables=["schema_context", "question"]
)

sql_synth_prompt = PromptTemplate(
    template=SQL_SYNTHESIS_PROMPT,
    input_variables=["question", "sql_query", "sql_results"]
)

def generate_and_execute_sql(question: str) -> Tuple[str, str, List[Dict[str, Any]]]:
    """
    Translates question to SQL, validates it, runs it against MySQL, and summarizes the result.
    Returns:
        (answer: str, clean_query: str, raw_results: List[dict])
    """
    api_key = settings.get_gemini_api_key()
    llm = ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        temperature=0.0,
        google_api_key=api_key
    )

    schema_context = get_database_schema_context()
    formatted_gen = sql_gen_prompt.format(
        schema_context=schema_context,
        question=question
    )

    # 1. Generate SQL with Gemini
    gen_response = llm.invoke(formatted_gen)
    raw_query = gen_response.content.strip()

    # 2. Validate SQL strictly
    is_valid, clean_query, err = validate_sql_query(raw_query)
    if not is_valid:
        error_msg = f"Security Error: Query generation failed safety validation. {err}"
        logger.warning(error_msg)
        return error_msg, raw_query, []

    # 3. Execute query on MySQL
    try:
        results = execute_select_query(clean_query)
    except Exception as e:
        logger.error(f"MySQL execution error: {e}")
        return f"Database Error: Could not execute query. {str(e)}", clean_query, []

    # 4. Synthesize natural language answer
    if not results:
        return "No records found matching your query criteria in the database.", clean_query, []

    formatted_synth = sql_synth_prompt.format(
        question=question,
        sql_query=clean_query,
        sql_results=str(results)
    )
    synth_response = llm.invoke(formatted_synth)
    answer = synth_response.content.strip()

    return answer, clean_query, results
