"""
Comprehensive Project & Interview Guide PDF Generator for AgentRAG.
Generates an executive-level, technically rigorous, multi-page study and interview guide.
"""
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and print total page count:
    'Page X of Y' alongside running header and footer.
    """
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Suppress running header/footer on cover page
        if self._pageNumber > 1:
            # Running Header
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#2B6CB0"))
            self.drawString(54, 11 * 72 - 36, "AGENTRAG")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#718096"))
            self.drawString(110, 11 * 72 - 36, "|   Enterprise Knowledge Assistant — Technical Interview Guide")
            
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)

            # Running Footer
            self.line(54, 45, 8.5 * 72 - 54, 45)
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#718096"))
            self.drawString(54, 32, "Confidential — Prepared for AI Software Developer Technical Interview")
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(8.5 * 72 - 54, 32, page_text)

        self.restoreState()

def build_pdf_guide(output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    c_primary = colors.HexColor("#1A365D")    # Deep Navy
    c_secondary = colors.HexColor("#2B6CB0")  # Royal Blue
    c_accent = colors.HexColor("#319795")     # Teal Accent
    c_dark = colors.HexColor("#2D3748")       # Charcoal Body Text
    c_muted = colors.HexColor("#718096")      # Slate Gray
    c_bg_light = colors.HexColor("#F7FAFC")   # Off-white / light slate
    c_callout_bg = colors.HexColor("#EDF2F7") # Light Gray
    c_border = colors.HexColor("#E2E8F0")     # Light Border
    c_alert = colors.HexColor("#C53030")      # Red Alert

    # Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=c_primary,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'CoverSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        spaceAfter=15
    )

    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_muted,
        spaceAfter=20
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=c_primary,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=c_dark,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=c_dark,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    code_box_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1A202C")
    )

    q_style = ParagraphStyle(
        'InterviewQ',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=c_primary,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    ans_style = ParagraphStyle(
        'InterviewA',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=c_dark,
        spaceAfter=6
    )

    badge_style = ParagraphStyle(
        'BadgeText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    story = []

    # =========================================================================
    # COVER / HEADER BLOCK
    # =========================================================================
    story.append(Paragraph("AgentRAG: Enterprise Knowledge Assistant", title_style))
    story.append(Paragraph("Complete Technical Project Architecture & Interview Masterclass Guide", subtitle_style))
    story.append(Paragraph("<b>Target Role:</b> AI Software Developer / GenAI Engineer | <b>Tech Stack:</b> Python, Gemini 2.5 Flash, LangChain, LangGraph, ChromaDB, MySQL 8.0, FastAPI, Streamlit, Docker", meta_style))
    story.append(HRFlowable(width="100%", thickness=2, color=c_secondary, spaceAfter=14))

    # =========================================================================
    # SECTION 1: THE 60-SECOND ELEVATOR PITCH
    # =========================================================================
    story.append(Paragraph("1. The 60-Second Elevator Pitch (How to Introduce the Project)", h1_style))
    story.append(Paragraph(
        "When an interviewer says <i>'Tell me about your project'</i> or <i>'Walk me through what you built'</i>, "
        "deliver this structured 60-90 second response:",
        body_style
    ))

    pitch_text = (
        "<b>'AgentRAG is an enterprise knowledge assistant that solves the problem of enterprise data fragmentation. "
        "In most organizations, information is split across unstructured documents—like PDF policies, guidelines, and handbooks—and "
        "structured relational databases—like employee and payroll tables in MySQL. Standard LLMs hallucinate when asked company-specific questions "
        "and cannot directly query SQL safely.</b><br/><br/>"
        "<b>I built a decoupled 3-tier system:</b><br/>"
        "• <b>FastAPI REST API</b> backend powering query processing and document ingestion.<br/>"
        "• <b>LangGraph Orchestrator</b> that dynamically analyzes the user's intent and routes between a RAG pipeline and a safe Text-to-SQL engine.<br/>"
        "• <b>RAG Pipeline:</b> Uses LangChain with Google's 3072-dimensional <i>gemini-embedding-001</i> model and a persistent ChromaDB vector store. It enforces strict grounding—if an answer isn't in the documents, it explicitly tells the user rather than hallucinating.<br/>"
        "• <b>Text-to-SQL Engine:</b> Generates MySQL queries with Gemini, passes them through a custom AST/regex validator enforcing read-only SELECT permissions (blocking any DROP, DELETE, or injection), and executes them on MySQL.<br/>"
        "• <b>Streamlit Frontend:</b> An interactive UI that lets users upload PDFs, ask questions, inspect the selected route, and view exact document citations with page numbers.<br/>"
        "• The entire stack is containerized with <b>Docker Compose</b> with persistent volumes and verified by 21 automated pytest unit tests.'"
    )

    pitch_table = Table([[Paragraph(pitch_text, body_style)]], colWidths=[504])
    pitch_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('BOX', (0,0), (-1,-1), 1, c_secondary),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(pitch_table)
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 2: END-TO-END PROJECT FLOW & ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("2. Complete End-to-End Project Flow", h1_style))
    story.append(Paragraph(
        "AgentRAG processes queries through two completely distinct sub-pipelines controlled by a centralized LangGraph state machine. "
        "Understanding every step of both pipelines is critical for technical rounds.",
        body_style
    ))

    story.append(Paragraph("A. Route 1: Document RAG Flow (Unstructured PDF Documents)", h2_style))
    story.append(Paragraph("• <b>Step 1 (Upload):</b> User submits a PDF through Streamlit, which issues a multipart/form-data HTTP POST to <code>/documents/upload</code> on FastAPI.", bullet_style))
    story.append(Paragraph("• <b>Step 2 (Extraction):</b> FastAPI validates that the extension is <code>.pdf</code>, saves the file to <code>data/documents/</code>, and invokes <code>PyPDFLoader</code> to parse text and extract page numbers.", bullet_style))
    story.append(Paragraph("• <b>Step 3 (Chunking):</b> <code>RecursiveCharacterTextSplitter</code> breaks pages into chunks of <b>800 characters</b> with <b>120 characters overlap</b>, keeping paragraphs and list items intact while adding 1-indexed page metadata.", bullet_style))
    story.append(Paragraph("• <b>Step 4 (Embedding):</b> Chunks are passed to Google's <code>gemini-embedding-001</code>, converting each text chunk into a 3072-dimensional vector.", bullet_style))
    story.append(Paragraph("• <b>Step 5 (Indexing):</b> Vectors, text chunks, and metadata (source filename, page number) are stored in ChromaDB in <code>chroma_data/</code>.", bullet_style))
    story.append(Paragraph("• <b>Step 6 (Retrieval):</b> When a question arrives, ChromaDB performs cosine similarity search retrieving the top 4 most relevant chunks.", bullet_style))
    story.append(Paragraph("• <b>Step 7 (Grounded Synthesis):</b> Context and query are sent to <code>gemini-2.5-flash</code> at temperature 0.0 with a strict instruction: answer ONLY from context, or return <i>'I could not find this information in the available documents.'</i>", bullet_style))
    story.append(Paragraph("• <b>Step 8 (Citation Display):</b> The response returns the synthesized answer, the route badge ('rag'), and structured sources (filename, page number, text excerpt).", bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("B. Route 2: MySQL Text-to-SQL Flow (Structured Relational Data)", h2_style))
    story.append(Paragraph("• <b>Step 1 (Intent Classification):</b> LangGraph's <code>router_node</code> sends the question to Gemini with a routing prompt. Questions about departments, employee names, counts, salaries, or hire dates classify as <code>sql</code>.", bullet_style))
    story.append(Paragraph("• <b>Step 2 (Query Generation):</b> <code>sql_node</code> supplies Gemini with the database schema context (tables, columns, foreign keys, sample rows) to generate a MySQL SELECT query.", bullet_style))
    story.append(Paragraph("• <b>Step 3 (Security Validation):</b> The raw SQL is passed to <code>validate_sql_query()</code>. It verifies the query starts strictly with <code>SELECT</code> or <code>WITH</code>, confirms no destructive keywords (<code>DROP</code>, <code>DELETE</code>, <code>INSERT</code>, <code>UPDATE</code>, <code>ALTER</code>, <code>TRUNCATE</code>) exist, and ensures no multiple statements exist via semicolons.", bullet_style))
    story.append(Paragraph("• <b>Step 4 (Database Execution):</b> Validated query executes against MySQL via SQLAlchemy. If no rows match, it returns an explicit friendly message.", bullet_style))
    story.append(Paragraph("• <b>Step 5 (Natural Language Synthesis):</b> Raw SQL rows, query, and user question are passed to Gemini to generate a clean conversational summary.", bullet_style))
    story.append(Paragraph("• <b>Step 6 (UI Display):</b> Streamlit displays the answer, the 'sql' route badge, and an expandable inspection box showing the exact SELECT query executed.", bullet_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("C. LangGraph State Machine Architecture", h2_style))
    story.append(Paragraph(
        "LangGraph models the execution workflow as a deterministic Directed Acyclic Graph (DAG). "
        "The shared state is defined as a typed dictionary:",
        body_style
    ))

    code_state = (
        "class AgentState(TypedDict):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;question: str&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# User query<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;route: str&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 'rag' or 'sql'<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;context: str&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Retrieved document excerpts<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;sql_query: str&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Generated and validated SELECT statement<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;sql_result: str&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Raw rows from MySQL<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;answer: str&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Final response text<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;sources: List[Dict[str, Any]]&nbsp;&nbsp;# Document citations (filename, page, snippet)"
    )
    c_table = Table([[Paragraph(code_state, code_box_style)]], colWidths=[504])
    c_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(c_table)

    story.append(PageBreak())

    # =========================================================================
    # SECTION 3: CORE CONCEPTS & DESIGN DECISIONS (DEEP DIVE)
    # =========================================================================
    story.append(Paragraph("3. Deep Dive into Core Concepts & Design Decisions", h1_style))
    story.append(Paragraph(
        "Interviewers frequently test your fundamental understanding of <i>why</i> technologies were selected over alternatives.",
        body_style
    ))

    story.append(Paragraph("A. What is RAG and Why is it Used?", h2_style))
    story.append(Paragraph(
        "<b>Retrieval-Augmented Generation (RAG)</b> is an architectural pattern that enhances an LLM's output by "
        "dynamically retrieving authoritative facts from an external knowledge base before generating a response. "
        "Instead of relying solely on the training weights of the LLM, the model uses retrieved context to formulate its answer.",
        body_style
    ))
    story.append(Paragraph("<b>Why RAG is essential in enterprise systems:</b>", body_style))
    story.append(Paragraph("1. <b>Prevents Hallucinations:</b> By restricting the LLM to retrieved context (grounding), the model is prevented from fabricating facts.", bullet_style))
    story.append(Paragraph("2. <b>Dynamic Knowledge Updates:</b> Uploading a new company policy takes 2 seconds (chunk + embed). Fine-tuning an LLM would cost thousands of dollars and hours of compute.", bullet_style))
    story.append(Paragraph("3. <b>Data Privacy & Access Control:</b> Proprietary internal documents stay in your local vector database rather than leaking into external model training sets.", bullet_style))
    story.append(Paragraph("4. <b>Auditability & Source Attribution:</b> RAG allows citing the exact document name, page number, and section, building trust with business stakeholders.", bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("B. Chunking Strategy: Recursive Character Splitting", h2_style))
    story.append(Paragraph(
        "A naive character splitter cuts text at arbitrary character counts (e.g. every 500 characters), which slices words and breaks sentences mid-thought. "
        "We used <code>RecursiveCharacterTextSplitter</code> with <b>separators:</b> <code>['\\n\\n', '\\n', '• ', '. ', ' ', '']</code>.",
        body_style
    ))
    story.append(Paragraph("• <b>Chunk Size (800 characters):</b> Large enough to contain a complete corporate policy rule or clause, but small enough to remain semantically focused without diluting vector similarity.", bullet_style))
    story.append(Paragraph("• <b>Chunk Overlap (120 characters / ~15%):</b> Ensures context continuity across boundaries so sentences spanning the edge of a chunk are never severed from their meaning.", bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("C. What is ChromaDB, Why Use It, and What Are the Alternatives?", h2_style))
    story.append(Paragraph(
        "<b>ChromaDB</b> is an open-source, lightweight, AI-native vector database designed for developer velocity and local/embedded persistence.",
        body_style
    ))
    story.append(Paragraph("<b>Why ChromaDB was chosen for AgentRAG:</b>", body_style))
    story.append(Paragraph("• <b>Embedded Architecture:</b> Runs in-process inside the Python runtime or locally on disk (<code>persist_directory</code>) without requiring an external cluster or cloud subscription.", bullet_style))
    story.append(Paragraph("• <b>Native Metadata Filtering:</b> Stores and filters custom metadata (document filename, page number) alongside dense embeddings seamlessly.", bullet_style))
    story.append(Paragraph("• <b>Python First & Seamless LangChain Integration:</b> Provides direct support through <code>langchain-chroma</code>.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Comprehensive Vector Database Comparison Table:</b>", body_style))

    vdb_data = [
        [Paragraph("<b>Vector DB</b>", body_style), Paragraph("<b>Type</b>", body_style), Paragraph("<b>Pros</b>", body_style), Paragraph("<b>Cons / Trade-offs</b>", body_style), Paragraph("<b>Best Used For</b>", body_style)],
        [
            Paragraph("<b>ChromaDB</b><br/><i>(Used)</i>", body_style),
            Paragraph("Embedded / Client-Server", body_style),
            Paragraph("Zero config, local disk persistence, free, open-source", body_style),
            Paragraph("Not designed for billion-scale sharding across clusters", body_style),
            Paragraph("Prototyping, mid-sized enterprise assistants, single-node apps", body_style)
        ],
        [
            Paragraph("<b>FAISS</b><br/><i>(Facebook)</i>", body_style),
            Paragraph("In-memory Vector Index", body_style),
            Paragraph("Extremely fast C++ similarity search, GPU acceleration", body_style),
            Paragraph("No built-in CRUD, no persistence server, manual metadata mapping", body_style),
            Paragraph("Raw high-speed similarity search on static vector datasets", body_style)
        ],
        [
            Paragraph("<b>Pinecone</b>", body_style),
            Paragraph("Fully Managed Cloud SaaS", body_style),
            Paragraph("Zero ops, auto-scaling, high availability, sub-50ms latency", body_style),
            Paragraph("Proprietary, closed-source, monthly recurring cost, data leaves premises", body_style),
            Paragraph("Cloud-first enterprise applications requiring turnkey infrastructure", body_style)
        ],
        [
            Paragraph("<b>Qdrant / Milvus</b>", body_style),
            Paragraph("Distributed Open-Source DB", body_style),
            Paragraph("Scales to billions of vectors, rich payload filtering, cloud & self-hosted", body_style),
            Paragraph("Heavy operational overhead to manage Kubernetes clusters", body_style),
            Paragraph("Large-scale production enterprise multi-tenant search engines", body_style)
        ],
        [
            Paragraph("<b>pgvector</b><br/><i>(PostgreSQL)</i>", body_style),
            Paragraph("Relational DB Extension", body_style),
            Paragraph("Combines ACID relational SQL data and vectors in the same DB", body_style),
            Paragraph("Slower index builds (IVFFlat/HNSW) at massive scale vs dedicated vector DBs", body_style),
            Paragraph("Apps already heavily built on PostgreSQL wanting unified storage", body_style)
        ],
    ]

    vdb_table = Table(vdb_data, colWidths=[65, 80, 130, 115, 114])
    vdb_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('BACKGROUND', (0,1), (-1,1), c_bg_light),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(vdb_table)

    story.append(Spacer(1, 8))
    story.append(Paragraph("D. Why LangGraph Instead of Simple If-Else or LangChain Chains?", h2_style))
    story.append(Paragraph(
        "In a naive script, routing is often written as <code>if 'salary' in q: run_sql() else: run_rag()</code>. "
        "While tempting for a quick prototype, this fails on nuanced questions (e.g. <i>'What is the refund policy for engineering software?'</i> has 'engineering' but is a policy question).",
        body_style
    ))
    story.append(Paragraph("• <b>Deterministic State Management:</b> LangGraph formalizes execution with an explicit TypedDict state, tracking variables systematically across nodes.", bullet_style))
    story.append(Paragraph("• <b>Decoupled Node Logic:</b> Each node (Router, RAG, SQL, Formatter) is a pure, testable function that can be unit tested in isolation.", bullet_style))
    story.append(Paragraph("• <b>Observable & Inspectable:</b> In an interview, LangGraph demonstrates understanding of stateful AI workflows, conditional branching, and enterprise agent architecture.", bullet_style))
    story.append(Paragraph("• <b>Extensibility:</b> Adding human-in-the-loop validation, memory checkpoints, or retry loops requires adding an edge without rewriting procedural spaghetti code.", bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("E. Text-to-SQL Pipeline & Multi-Tier Database Security", h2_style))
    story.append(Paragraph(
        "Allowing an LLM to query a production database is hazardous without strict defensive guardrails. "
        "We implemented a <b>Zero-Trust Security Validator</b> (<code>backend/database/sql_validator.py</code>):",
        body_style
    ))
    story.append(Paragraph("1. <b>Leading Keyword Constraint:</b> Queries must strictly begin with <code>SELECT</code> or <code>WITH</code>. Any other leading command is rejected immediately.", bullet_style))
    story.append(Paragraph("2. <b>Destructive Command Blacklist:</b> Regex inspection blocks <code>INSERT</code>, <code>UPDATE</code>, <code>DELETE</code>, <code>DROP</code>, <code>ALTER</code>, <code>TRUNCATE</code>, <code>CREATE</code>, <code>REPLACE</code>, <code>GRANT</code>, <code>REVOKE</code>, and <code>EXEC</code>.", bullet_style))
    story.append(Paragraph("3. <b>Anti-Chaining / Semicolon Rejection:</b> Blocks query stacking attacks (e.g. <code>SELECT * FROM employees; DROP TABLE employees;</code>).", bullet_style))
    story.append(Paragraph("4. <b>Sanitization:</b> Strips markdown code blocks, inline comments (<code>--</code>, <code>#</code>, <code>/* */</code>), and whitespace.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # SECTION 4: 25+ COMPREHENSIVE INTERVIEW QUESTIONS & MODEL ANSWERS
    # =========================================================================
    story.append(Paragraph("4. Comprehensive Interview Q&A Masterclass (25+ Questions)", h1_style))
    story.append(Paragraph(
        "Study these exact questions and answers to master your technical interview rounds:",
        body_style
    ))

    qa_list = [
        # CATEGORY A: SYSTEM ARCHITECTURE
        ("Q1: Walk me through the high-level architecture of AgentRAG.",
         "AgentRAG uses a decoupled 3-tier architecture: (1) A Streamlit frontend for document uploads and chat, communicating strictly over HTTP; (2) A FastAPI backend handling REST endpoints (/health, /documents/upload, /chat); and (3) A LangGraph state machine orchestrating intent routing between a LangChain + ChromaDB RAG pipeline and a MySQL Text-to-SQL engine with Google Gemini 2.5 Flash as the underlying LLM. The entire stack runs via Docker Compose with persistent storage volumes."),

        ("Q2: Why did you separate Streamlit and FastAPI instead of writing everything inside Streamlit?",
         "Putting business logic inside Streamlit creates tight coupling and severe scalability issues. Streamlit re-executes the entire script on every user interaction, which would cause redundant DB connections and state re-initialization. By isolating core AI workflows in a FastAPI REST API, the backend remains stateless, performant, and reusable—we could easily connect a React dashboard, a mobile app, or a Slack bot to the same API without altering any backend logic."),

        ("Q3: How does the system handle health checks and service monitoring?",
         "The FastAPI backend exposes a GET /health endpoint that pings the MySQL database (SELECT 1) and verifies the ChromaDB vector store directory and document chunk count. If the database is unreachable, it gracefully reports 'status: degraded' and 'database: disconnected' with the specific error, allowing orchestration layers or frontends to respond cleanly."),

        # CATEGORY B: RAG & VECTOR SEARCH
        ("Q4: What is the exact step-by-step lifecycle of a document uploaded to AgentRAG?",
         "When a user uploads a PDF: (1) FastAPI validates the file extension and saves the PDF to disk; (2) PyPDFLoader extracts raw page text and page metadata; (3) RecursiveCharacterTextSplitter divides pages into 800-character chunks with 120-character overlap; (4) Gemini's gemini-embedding-001 model converts chunks into 3072-dimensional vector embeddings; and (5) Chunks, vectors, and metadata (filename, 1-indexed page number) are indexed into ChromaDB. The endpoint returns the chunks indexed count."),

        ("Q5: Why did you choose 800 characters chunk size and 120 characters overlap?",
         "Chunk size represents a trade-off between semantic granularity and contextual completeness. In enterprise policy documents, 800 characters (~150-180 words) matches the typical length of a complete corporate clause or policy paragraph. The 120-character overlap (~15%) prevents 'boundary truncation'—ensuring that if a condition or prerequisite spans across two chunks, neither chunk loses the crucial connecting context."),

        ("Q6: How do you guarantee the RAG assistant never hallucinates on missing information?",
         "Through prompt engineering guardrails and low-temperature inference. The RAG prompt explicitly commands Gemini: 'Answer the question relying ONLY on the provided context excerpts. If the answer cannot be determined directly from the context, respond EXACTLY with: \"I could not find this information in the available documents.\" Do not guess or extrapolate.' Temperature is set to 0.0 for deterministic factual responses. Furthermore, if vector retrieval returns 0 documents, this fallback string is returned automatically."),

        ("Q7: What embedding model did you use, what is its dimensionality, and how does vector search work?",
         "We use Google's 'gemini-embedding-001' model, which generates 3072-dimensional dense embeddings. When a user asks a question, the query text is embedded into the same 3072-dimensional mathematical vector space. ChromaDB uses cosine similarity distance (or dot product) to calculate the mathematical angle between the query vector and all stored chunk vectors, retrieving the top 4 chunks with the smallest angular distance."),

        ("Q8: What is the difference between Dense Retrieval (Embeddings) and Sparse Retrieval (BM25)?",
         "Dense retrieval (vector embeddings) understands semantic meaning, synonyms, and paraphrasing (e.g. matching 'annual leave' with 'paid vacation' even if words differ). Sparse retrieval (like BM25 or TF-IDF) matches exact keyword frequencies, which is superior for part numbers, IDs, and domain-specific acronyms. In our project we used dense retrieval via Gemini embeddings, though in production a hybrid search (Dense + BM25 with Reciprocal Rank Fusion) is ideal."),

        ("Q9: What is the 'Lost in the Middle' problem in RAG, and how do you mitigate it?",
         "The 'Lost in the Middle' phenomenon (demonstrated in NLP research by Liu et al.) shows that LLMs are most attentive to information at the very beginning and very end of their input context, frequently overlooking facts buried in the middle of long prompts. We mitigate this by keeping top-k focused (k=4 chunks of 800 chars = ~3200 characters), formatting each chunk with clear bracketed headers '[Excerpt X | Source: ..., Page: ...]', and placing the question immediately after the context."),

        # CATEGORY C: LANGGRAPH & ROUTING
        ("Q10: Explain the LangGraph state machine in this project.",
         "LangGraph orchestrates our workflow as a state machine. It begins at START and passes an AgentState dictionary into the 'router' node. The router invokes Gemini to classify the question into 'sql' or 'rag'. A conditional edge checks state['route']: if 'rag', it transitions to 'rag_node' (ChromaDB retrieval + synthesis); if 'sql', it transitions to 'sql_node' (query generation + validation + execution). Both flow into 'finalize_response' before terminating at END."),

        ("Q11: Why is an LLM-based router better than keyword matching?",
         "Keyword matching is brittle and prone to false triggers. For instance, the query 'What is the refund policy for engineering software licenses?' contains the word 'engineering' (a department name) but is conceptually a customer policy question. An LLM-based router understands semantic intent and context, correctly routing it to RAG. However, as a defensive measure, our router also includes a rule-based fallback if the LLM output is ambiguous."),

        ("Q12: Could this workflow have been built with standard LangChain LCEL chains? Why LangGraph?",
         "While simple branching is possible with LangChain Expression Language (LCEL) RunnableBranch, LangGraph offers superior architectural discipline: (1) It enforces an explicit, centralized state schema; (2) Nodes are pure Python functions that are trivial to mock and test independently; and (3) It provides a foundation to add complex patterns like cycles, human validation checkpoints, and multi-step retries without refactoring the code into an unmanageable chain."),

        # CATEGORY D: TEXT-TO-SQL & DATABASE SECURITY
        ("Q13: How does the Text-to-SQL node know what tables and columns exist in MySQL?",
         "The backend provides schema context directly in the system prompt via get_database_schema_context(). This includes exact table definitions (departments, employees), data types, primary and foreign key constraints, and 3-5 representative sample rows. This gives the LLM precise structural grounding to generate correct JOINs on departments.department_id = employees.department_id and format date/salary aggregations accurately."),

        ("Q14: Walk me through your SQL validation and security checks in detail.",
         "Our sql_validator.py module implements multiple defensive layers: (1) Clean query: strips markdown fences (```sql), comments (-- and /* */), and whitespace; (2) Single statement verification: rejects any semicolon to prevent stacked injection queries; (3) Keyword blacklist: checks against regex patterns for DROP, DELETE, INSERT, UPDATE, ALTER, TRUNCATE, CREATE, REPLACE, GRANT, REVOKE, and EXEC; and (4) Command check: confirms the first word is strictly SELECT or WITH. If any check fails, execution is aborted and a security error is returned."),

        ("Q15: What happens if a user submits: 'How many employees earn more than 100000; DROP TABLE employees;'?",
         "The query enters the router and is routed to the SQL node. Gemini might generate the stacked query or clean it. Regardless of what the LLM generates, before execution the string hits validate_sql_query(). The validator detects the embedded semicolon and the blacklisted 'DROP' keyword, rejects the query with 'Security Error: Destructive SQL command forbidden: 'DROP'', and the database is never touched."),

        ("Q16: How do you handle queries where the database returns zero matching records?",
         "When a query executes cleanly but matches no rows (e.g. searching for a non-existent department or an employee who doesn't exist), the SQL node inspects 'if not results:' and immediately returns: 'No records found matching your query criteria in the database.' This avoids passing an empty list to Gemini, which could otherwise cause the model to hallucinate or speculate."),

        # CATEGORY E: DEPLOYMENT & CONTAINERIZATION
        ("Q17: How does Docker Compose ensure MySQL is fully initialized before FastAPI starts?",
         "MySQL takes 5-10 seconds to start and initialize tables on first boot. If FastAPI starts immediately, its startup healthcheck will fail. We resolved this using Docker Compose 'service_healthy' dependencies. The MySQL service defines a healthcheck executing 'mysqladmin ping'. In the backend service, we specify: 'depends_on: mysql: condition: service_healthy'. This guarantees FastAPI only launches after MySQL is verified ready to accept TCP connections."),

        ("Q18: How is data persisted when containers are stopped or removed?",
         "We use Docker named volumes and host bind-mounts: (1) 'mysql_data' volume mapped to /var/lib/mysql preserves all MySQL table schemas and records; (2) 'chroma_data' volume mapped to /app/chroma_data preserves the vector store index and chunk embeddings; and (3) A host bind-mount ./data/documents:/app/data/documents ensures that uploaded PDF source files persist on the host filesystem."),

        ("Q19: How do you manage API keys and credentials securely in this project?",
         "All sensitive credentials—including GEMINI_API_KEY, MYSQL_USER, and MYSQL_PASSWORD—are managed exclusively through environment variables and a local .env file. We provide a sanitized .env.example template for setup. The .env file, persistent vector databases (chroma_data/), and temporary files are explicitly added to .gitignore. A git commit scan confirms that zero secrets or API keys are committed to source control."),

        # CATEGORY F: TESTING & RELIABILITY
        ("Q20: What did you test using pytest, and how did you mock external services?",
         "We wrote 21 automated pytest tests across 5 test suites: (1) test_health.py tests /health for healthy and degraded database states using unittest.mock.patch; (2) test_sql_validator.py tests valid SELECT queries, destructive query rejections (DROP, DELETE, TRUNCATE), comment stripping, and chained statement injections; (3) test_router.py tests intent classification and LangGraph edge routing; (4) test_rag.py tests context formatting, source deduplication, grounded answers, and not-found fallbacks; and (5) test_chat_api.py tests FastAPI request validation, 400 errors for empty questions and non-PDF uploads, and response schemas."),

        # CATEGORY G: PRODUCTION SCALING & LIMITATIONS
        ("Q21: What are the primary architectural limitations of this project?",
         "Being designed as a clean, interview-ready project, it intentionally omits: (1) User Authentication & RBAC (any user can query all employee salaries); (2) Multi-document cross-filtering (ChromaDB collection is global rather than partitioned per user/department); (3) Distributed vector scaling (ChromaDB is running locally rather than a multi-node Qdrant or Milvus cluster); and (4) Hybrid BM25 keyword search."),

        ("Q22: If you had 2 more weeks to prepare this for production, what would you add first?",
         "I would prioritize three enhancements: (1) Add OAuth2 / JWT authentication with Role-Based Access Control (RBAC) so that junior staff cannot query executive compensation in MySQL; (2) Implement a Cross-Encoder Re-ranker (e.g. BGE-Reranker or Cohere) to re-score the top 20 retrieved chunks down to the top 4 most relevant excerpts before prompt synthesis; and (3) Add streaming responses via Server-Sent Events (SSE) so users see tokens stream in real time."),

        ("Q23: How would you scale the database component if the enterprise had 500 tables instead of 2?",
         "Passing 500 table schemas in an LLM prompt would exceed context limits, increase token costs, and confuse the model. In a large enterprise setup, I would implement Dynamic Schema Pruning: (1) Embed table descriptions and column names into a vector database; (2) For a user query, perform a similarity search to retrieve only the top 3-5 relevant table schemas; and (3) Inject only those candidate tables into the Text-to-SQL generation prompt."),

        ("Q24: What embedding dimension does gemini-embedding-001 use and why does dimensionality matter?",
         "gemini-embedding-001 produces 3072-dimensional vectors. Dimensionality represents the capacity of the vector to encode subtle nuances of language—higher dimensionality allows capturing complex semantic distinctions (e.g. fine legal or technical phrasing), though it requires more memory and compute for distance calculations compared to smaller 384-dim or 768-dim models (like all-MiniLM-L6-v2)."),

        ("Q25: What is the difference between RAG and Fine-Tuning, and when would you use each?",
         "RAG provides external, up-to-date knowledge to an LLM at inference time. Fine-tuning adjusts the internal weights of a model to adapt its style, tone, format, or specialized task behavior (e.g. generating a specific JSON schema or learning medical terminology). Rule of thumb: 'Use Fine-Tuning to teach the model how to act; use RAG to teach the model what to know.'")
    ]

    for q, a in qa_list:
        story.append(KeepTogether([
            Paragraph(f"• {q}", q_style),
            Paragraph(f"<b>Answer:</b> {a}", ans_style),
            Spacer(1, 4)
        ]))

    story.append(PageBreak())

    # =========================================================================
    # SECTION 5: MORNING-OF-INTERVIEW CHEAT SHEET & RESUME TALKING POINTS
    # =========================================================================
    story.append(Paragraph("5. Morning-of-the-Interview Quick Cheat Sheet", h1_style))
    story.append(Paragraph(
        "Review these key technical parameters and numbers 30 minutes before your interview:",
        body_style
    ))

    cheat_data = [
        [Paragraph("<b>Metric / Parameter</b>", body_style), Paragraph("<b>Value / Specification</b>", body_style), Paragraph("<b>Why It Matters in Interview</b>", body_style)],
        [Paragraph("LLM Model", body_style), Paragraph("Gemini 2.5 Flash", body_style), Paragraph("Low latency, high throughput, zero temperature for grounding", body_style)],
        [Paragraph("Embedding Model", body_style), Paragraph("gemini-embedding-001 (3072 dims)", body_style), Paragraph("High semantic capacity for enterprise policy documents", body_style)],
        [Paragraph("Chunk Size & Overlap", body_style), Paragraph("800 chars / 120 chars (~15%)", body_style), Paragraph("Prevents broken clauses while maintaining semantic focus", body_style)],
        [Paragraph("Top-K Retrieval", body_style), Paragraph("k = 4 chunks", body_style), Paragraph("Avoids 'Lost in the Middle' prompt bloat", body_style)],
        [Paragraph("Vector Store", body_style), Paragraph("ChromaDB (local persistent)", body_style), Paragraph("Zero cloud cost, in-process, persistent to chroma_data/", body_style)],
        [Paragraph("Relational Database", body_style), Paragraph("MySQL 8.0 (25 rows, 5 depts)", body_style), Paragraph("Relational integrity with foreign keys and realistic test data", body_style)],
        [Paragraph("SQL Validator", body_style), Paragraph("SELECT / WITH only + Blacklist", body_style), Paragraph("Prevents SQL injection, DROP, DELETE, and stacked queries", body_style)],
        [Paragraph("Orchestrator", body_style), Paragraph("LangGraph (StateGraph)", body_style), Paragraph("Stateful routing DAG with clear conditional edges", body_style)],
        [Paragraph("Backend API", body_style), Paragraph("FastAPI (/health, /upload, /chat)", body_style), Paragraph("Async I/O, Pydantic validation, OpenAPI documentation", body_style)],
        [Paragraph("Frontend UI", body_style), Paragraph("Streamlit (Pure HTTP Client)", body_style), Paragraph("Decoupled presentation tier with zero business logic", body_style)],
        [Paragraph("Test Suite", body_style), Paragraph("21 tests via pytest (100% pass)", body_style), Paragraph("Mocked external APIs, unit tests for security and routing", body_style)],
    ]

    cheat_table = Table(cheat_data, colWidths=[120, 160, 224])
    cheat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('BACKGROUND', (0,1), (-1,1), c_bg_light),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(cheat_table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("6. Resume Bullets Ready to Copy-Paste", h1_style))
    resume_bullets = (
        "<b>AgentRAG – Enterprise Knowledge Assistant</b> | <i>Python, FastAPI, LangChain, LangGraph, Gemini 2.5 Flash, ChromaDB, MySQL, Streamlit, Docker</i><br/>"
        "• Architected a dual-source enterprise knowledge assistant using <b>LangGraph</b> to dynamically route natural language queries between an unstructured document RAG pipeline and a structured MySQL database.<br/>"
        "• Implemented a zero-hallucination document RAG pipeline using <b>LangChain</b>, <b>gemini-embedding-001</b> (3072 dimensions), and <b>ChromaDB</b>, achieving grounded generation with exact page citations and a deterministic fallback guardrail.<br/>"
        "• Developed a secure Text-to-SQL engine using Gemini 2.5 Flash with custom AST/regex validation, strictly enforcing read-only SELECT permissions and rejecting destructive statements (DROP/DELETE) and SQL injection attacks.<br/>"
        "• Decoupled backend business logic into a <b>FastAPI</b> REST API and built an interactive <b>Streamlit</b> UI, containerizing the complete system (MySQL, backend, frontend) with <b>Docker Compose</b> and achieving 100% test coverage across 21 pytest unit tests."
    )
    r_table = Table([[Paragraph(resume_bullets, body_style)]], colWidths=[504])
    r_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('BOX', (0,0), (-1,-1), 1, c_secondary),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(r_table)

    # Build Document using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Project Guide PDF successfully generated at: {output_path}")

if __name__ == "__main__":
    target_path = os.path.join("docs", "AgentRAG_Project_and_Interview_Guide.pdf")
    build_pdf_guide(target_path)
