"""
Intent Classifier / Query Router Module.
Determines whether a user query requires RAG (document search) or SQL (structured database).
"""
import re
import logging
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config import settings

logger = logging.getLogger(__name__)

ROUTER_PROMPT = """You are a precise query router for an enterprise assistant.
Classify the user's question into exactly ONE of two routes:

1. 'sql' -> For questions about structured data in the employee database:
   - Specific employees (names, designations, salaries, joining dates)
   - Departments, department counts, staff numbers, averages, totals
   - Examples: "How many employees are in Engineering?", "What is the average salary?", "Who is the HR director?"

2. 'rag' -> For questions about unstructured company documentation, policies, and guidelines:
   - Leave policy, sick days, vacation, parental leave
   - Working hours, core hours, attendance, lunch break
   - Remote work policy, equipment stipend, internet reimbursement
   - Benefits, 401(k), health insurance, wellness budget
   - Customer refund policy, license cancellation rules
   - Examples: "What is the leave policy?", "Can I work remotely?", "What is the refund policy?"

Return ONLY the single lowercase word: 'sql' or 'rag'. Do not add punctuation, markdown, or explanation.

Question: {question}
Route:"""

router_prompt_template = PromptTemplate(
    template=ROUTER_PROMPT,
    input_variables=["question"]
)

def classify_query_route(question: str) -> str:
    """
    Classifies a question into 'sql' or 'rag'.
    Uses Gemini LLM with safe fallback parsing.
    """
    api_key = settings.get_gemini_api_key()
    llm = ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        temperature=0.0,
        google_api_key=api_key
    )

    formatted = router_prompt_template.format(question=question)
    response = llm.invoke(formatted)
    raw_decision = response.content.strip().lower()

    # Clean and match exact route keyword
    if "sql" in raw_decision and "rag" not in raw_decision:
        return "sql"
    elif "rag" in raw_decision and "sql" not in raw_decision:
        return "rag"
    
    # Keyword fallback if LLM gave verbose response
    sql_keywords = ["salary", "employee", "employees", "department", "departments", "designation", "hired", "joined", "count", "average", "earning"]
    if any(re.search(rf"\b{kw}\b", question.lower()) for kw in sql_keywords):
        return "sql"

    return "rag"
