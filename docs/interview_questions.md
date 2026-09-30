# AgentRAG – Technical Interview Questions & Answers

This guide contains **20 project-specific interview questions and concise answers** designed for freshers and junior AI engineers to confidently explain the **AgentRAG** project in technical interviews.

---

### 1. What is AgentRAG and what problem does it solve?
**Answer:**  
AgentRAG is an enterprise knowledge assistant that unifies two distinct corporate data sources:
1. **Unstructured documents** (e.g., employee handbooks, policies, FAQs) using a RAG pipeline with ChromaDB and Gemini.
2. **Structured tabular data** (e.g., employee directories, departments, payroll records) using an automated Text-to-SQL pipeline over MySQL.

It uses **LangGraph** to classify user intent and route queries dynamically so users don't need to know where the data is stored.

---

### 2. Walk me through the high-level architecture of the system.
**Answer:**  
The application has a decoupled 3-tier architecture:
- **Frontend:** Streamlit web application providing document upload, query input, and formatted responses (answer, route badge, document sources, and inspected SQL).
- **Backend:** FastAPI REST API exposing `/health`, `/documents/upload`, and `/chat`.
- **Workflow & Knowledge Layer:** LangGraph orchestrating state routing, ChromaDB for vector retrieval, MySQL for relational data, and Google Gemini 2.5 Flash for reasoning and generation.
- **Infrastructure:** Docker and Docker Compose containerizing MySQL, FastAPI, and Streamlit with persistent volume mounts.

---

### 3. Why did you use LangGraph instead of a hardcoded `if-else` or single prompt?
**Answer:**  
LangGraph models query processing as a **State Machine (DAG)** with explicit state, nodes, and conditional edges:
- **Explicit State:** The TypedDict `AgentState` tracks the question, route, retrieved context, SQL query, raw database rows, sources, and final answer.
- **Separation of Concerns:** Router, RAG retriever, and SQL executor are independent nodes.
- **Extensibility:** If we later want to add web search, human approval loops, or fallback retries, LangGraph allows adding nodes and edges without rewriting linear procedural logic.

---

### 4. How does the LangGraph Router decide between RAG and SQL?
**Answer:**  
The `router_node` calls Gemini with a focused system prompt classifying user intent into `"rag"` or `"sql"`:
- Queries regarding specific employees, salaries, counts, or departments map to `sql`.
- Queries regarding corporate policies, working hours, benefits, or refunds map to `rag`.

To ensure reliability, we implement a defensive keyword-based fallback if the model returns unexpected tokens, ensuring deterministic routing.

---

### 5. What fields are tracked in your LangGraph State?
**Answer:**  
We use a `TypedDict` containing:
- `question`: Original user question string.
- `route`: The determined path (`"rag"` or `"sql"`).
- `context`: Combined text excerpts from retrieved document chunks.
- `sql_query`: Validated SELECT query generated for SQL route.
- `sql_result`: Stringified rows returned from MySQL.
- `answer`: Grounded natural language response for the user.
- `sources`: List of dictionaries containing `source` filename, `page` number, and excerpt.

---

### 6. Walk me through your RAG pipeline from PDF upload to answer generation.
**Answer:**  
1. **Upload:** User submits a PDF via Streamlit, sent via HTTP multipart to FastAPI `POST /documents/upload`.
2. **Extraction:** `PyPDFLoader` extracts text and page metadata.
3. **Chunking:** `RecursiveCharacterTextSplitter` divides text into 800-character chunks with a 120-character overlap to preserve semantic context across chunk boundaries.
4. **Embedding:** `GoogleGenerativeAIEmbeddings` (`gemini-embedding-001`) converts chunks into 3072-dimensional vector embeddings.
5. **Storage:** Chunks and embeddings are stored persistently in ChromaDB.
6. **Retrieval:** Top-4 chunks are retrieved using vector cosine similarity.
7. **Synthesis:** Gemini generates an answer grounded strictly in the retrieved excerpts.

---

### 7. Why did you use `RecursiveCharacterTextSplitter` instead of splitting by raw character count?
**Answer:**  
`RecursiveCharacterTextSplitter` attempts to keep paragraphs (`\n\n`), sentences (`\n`, `. `), and bullet points (`• `) together before falling back to words and characters. This preserves syntactic boundaries and semantic meaning, which is critical for policy documents where fragmented sentences lead to incorrect retrieval or lost context.

---

### 8. Why choose ChromaDB as the vector database?
**Answer:**  
ChromaDB is lightweight, open-source, embedded, and provides native persistence directly to disk without requiring external server clusters or cloud API keys. For a single-node enterprise assistant or interview demonstration, ChromaDB offers fast vector search with zero infrastructure overhead.

---

### 9. How do you guarantee the RAG system never hallucinates?
**Answer:**  
Through **strict grounding prompts** and **retrieval verification**:
- The prompt explicitly instructs Gemini: *"Answer the question relying ONLY on the provided context excerpts. If the answer cannot be determined directly from the context, respond EXACTLY with: 'I could not find this information in the available documents.' Do not extrapolate or bring in outside knowledge."*
- Temperature is set to `0.0` for deterministic, factual outputs.
- If the vector retriever finds 0 documents or if information is absent, the fallback message is returned automatically.

---

### 10. How does your Text-to-SQL pipeline work?
**Answer:**  
1. Gemini receives the user's question alongside a concise schema description of `departments` and `employees` (table names, columns, types, foreign keys, and sample rows).
2. Gemini generates an executable MySQL SELECT query.
3. The query passes through our custom `validate_sql_query` security validator.
4. The validated query executes via SQLAlchemy on MySQL.
5. The result rows, executed SQL, and original question are passed to Gemini to synthesize a concise natural language explanation.

---

### 11. How do you prevent SQL injection and protect against destructive queries?
**Answer:**  
We employ multi-layer security validation:
1. **Leading Command Restriction:** Query must start strictly with `SELECT` or `WITH` (for common table expressions).
2. **Keyword Blacklist:** Rejects queries containing `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `REPLACE`, `GRANT`, `REVOKE`, `EXEC`, or `OUTFILE`.
3. **Multiple Statement Block:** Rejects queries with semicolons separating chained commands (`SELECT 1; DROP TABLE...`).
4. **Sanitization:** Strips markdown code blocks, inline comments (`--`, `/* */`), and trailing semicolons before validation.

---

### 12. What happens if a user submits: `DROP TABLE employees;`?
**Answer:**  
The query router recognizes it as a database inquiry and forwards it to the SQL node. However, before execution, `validate_sql_query()` scans the string, detects the forbidden `DROP` keyword, blocks execution, and returns:
`Security Error: Query generation failed safety validation. Destructive SQL command forbidden: 'DROP'.`
The database remains untouched.

---

### 13. How does the system handle database queries that return empty results?
**Answer:**  
If a valid SELECT query yields 0 rows (e.g., searching for an employee named "Batman"), the SQL node detects `if not results:` and gracefully returns:  
`"No records found matching your query criteria in the database."`  
This avoids hallucinations or confusing empty outputs.

---

### 14. Why did you choose FastAPI over Flask or Django?
**Answer:**  
- **Asynchronous performance:** Native `async/await` support suitable for I/O-bound LLM API calls and database connections.
- **Pydantic Validation:** Automatic request body parsing, type enforcement, and auto-generated error responses.
- **Interactive Documentation:** Built-in OpenAPI Swagger UI at `/docs` simplifies API testing and demonstration.
- **Lightweight:** No bloated ORM overhead like Django, but more modern and typed than Flask.

---

### 15. Why decouple Streamlit from FastAPI instead of writing everything in Streamlit?
**Answer:**  
Decoupling provides **clean separation of concerns**:
- Streamlit acts purely as a presentation layer handling UI widgets and rendering.
- FastAPI encapsulates business logic, LangGraph workflows, vector store connections, and database execution.
- If we later decide to build a Mobile App, Slack bot, or Teams integration, they can consume the exact same FastAPI endpoints without modifying core logic.

---

### 16. How does your Docker Compose setup ensure services start in the correct order?
**Answer:**  
MySQL takes several seconds to initialize on startup. If the backend connects before MySQL is ready, it crashes. We solve this using **Docker Healthchecks**:
- The `mysql` container defines a healthcheck executing `mysqladmin ping`.
- The `backend` container specifies:
  ```yaml
  depends_on:
    mysql:
      condition: service_healthy
  ```
- This ensures FastAPI only starts after MySQL reports healthy and ready to accept connections.

---

### 17. How do you persist data in MySQL and ChromaDB across container restarts?
**Answer:**  
We configure named volumes in `docker-compose.yml`:
- `mysql_data:/var/lib/mysql`: Preserves all MySQL tables, indexes, and seeded employee records.
- `chroma_data:/app/chroma_data`: Preserves ChromaDB vector indexes and document chunk embeddings.
- `./data/documents:/app/data/documents`: Bind-mounts uploaded PDFs so raw source documents survive restarts.

---

### 18. Which Gemini models did you use and why?
**Answer:**  
- **Chat & Reasoning:** `gemini-2.5-flash` for high-speed inference, strong reasoning capabilities for routing and SQL generation, and low latency.
- **Embeddings:** `gemini-embedding-001` (3072 dimensions) providing semantic representation tailored for enterprise retrieval.

---

### 19. What edge case or issue did you encounter during development and how did you resolve it?
**Answer:**  
When working with Google GenAI SDK v2 / `langchain-google-genai` 4.4, legacy embedding model references (`models/text-embedding-004`) resulted in a `404 NOT_FOUND` under the new API version. By querying the `client.models.list()` API, I identified that the supported embedding model is `gemini-embedding-001`. I updated the configuration and verified end-to-end vector indexing and similarity retrieval.

---

### 20. If you were deploying this to production, what improvements would you make?
**Answer:**  
1. **User Authentication & RBAC:** Add OAuth2/JWT authentication so employees can only query data matching their role (e.g., hiding individual executive salaries).
2. **Hybrid Search (BM25 + Dense):** Combine semantic vector search with keyword-based BM25 reciprocal rank fusion (RRF) for exact policy code lookups.
3. **Query Re-ranking:** Add a cross-encoder re-ranker (e.g., Cohere or BGE) to score retrieved chunks before passing to LLM.
4. **Read-only MySQL Database User:** Enforce read-only permissions directly at the MySQL user privilege level (`GRANT SELECT ON agentrag_db.* TO 'rag_readonly'@'%'`).
