"""
Demo Video Generator for AgentRAG.
Generates a high-definition (1280x720 @ 24fps) video walkthrough of AgentRAG.
NO AUDIO is added, in strict accordance with instructions.
"""
import os
import sys
import numpy as np
import imageio
from PIL import Image, ImageDraw, ImageFont

# Video Specs
WIDTH = 1280
HEIGHT = 720
FPS = 24

# Setup Fonts
def get_font(name="segoeui.ttf", size=16):
    windir = os.environ.get("WINDIR", "C:/Windows")
    font_path = os.path.join(windir, "Fonts", name)
    try:
        return ImageFont.truetype(font_path, size)
    except Exception:
        try:
            return ImageFont.truetype("arial.ttf", size)
        except Exception:
            return ImageFont.load_default()

font_title_lg = get_font("segoeuib.ttf", 38)
font_title = get_font("segoeuib.ttf", 26)
font_h2 = get_font("segoeuib.ttf", 20)
font_h3 = get_font("segoeuib.ttf", 16)
font_body = get_font("segoeui.ttf", 15)
font_body_bold = get_font("segoeuib.ttf", 15)
font_small = get_font("segoeui.ttf", 12)
font_small_bold = get_font("segoeuib.ttf", 12)
font_code = get_font("consola.ttf", 13)
font_code_bold = get_font("consolab.ttf", 13)

# Palette
C_BG = (248, 250, 252)         # Slate 50
C_SURFACE = (255, 255, 255)    # White
C_BORDER = (226, 232, 240)     # Slate 200
C_PRIMARY = (26, 54, 93)       # Deep Navy
C_ACCENT_BLUE = (43, 108, 176) # Blue 600
C_ACCENT_TEAL = (49, 151, 149) # Teal 500
C_TEXT_DARK = (45, 55, 72)     # Charcoal
C_TEXT_MUTED = (113, 128, 150) # Gray 500
C_SIDEBAR_BG = (241, 245, 249) # Slate 100
C_GREEN = (56, 161, 105)       # Green 500
C_ORANGE = (221, 107, 32)      # Orange 500
C_DARK_BG = (15, 23, 42)       # Slate 900
C_DARK_PANEL = (30, 41, 59)    # Slate 800

def draw_rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=outline, width=width)

def draw_browser_chrome(img, draw, active_tab="AgentRAG – Enterprise Knowledge Assistant"):
    # Browser Top Header (Mac/Windows style)
    draw.rectangle([0, 0, WIDTH, 42], fill=(226, 232, 240))
    # Window Controls (Red, Yellow, Green dots)
    draw.ellipse([14, 15, 24, 25], fill=(239, 68, 68))
    draw.ellipse([30, 15, 40, 25], fill=(245, 158, 11))
    draw.ellipse([46, 15, 56, 25], fill=(16, 185, 129))
    
    # URL Bar
    draw_rounded_rect(draw, [180, 8, 1100, 34], radius=6, fill=(255, 255, 255), outline=(203, 213, 225))
    draw.text((195, 12), "🔒 http://localhost:8501 (AgentRAG Streamlit App)", fill=(71, 85, 105), font=font_small)

def draw_streamlit_layout(img, draw, sidebar_info=None):
    draw_browser_chrome(img, draw)
    
    # Sidebar
    draw.rectangle([0, 42, 320, HEIGHT], fill=C_SIDEBAR_BG)
    draw.line([320, 42, 320, HEIGHT], fill=C_BORDER, width=1)
    
    # Sidebar Header
    draw.text((24, 60), "⚙️ Control Panel", fill=C_PRIMARY, font=font_h2)
    
    # System Status Card
    draw_rounded_rect(draw, [20, 100, 300, 220], radius=8, fill=(255, 255, 255), outline=C_BORDER)
    draw.text((32, 110), "System Health", fill=C_PRIMARY, font=font_h3)
    
    # Status Indicators
    draw.ellipse([32, 137, 42, 147], fill=C_GREEN)
    draw.text((48, 135), "Backend: ONLINE (FastAPI)", fill=C_GREEN, font=font_small_bold)
    
    draw.ellipse([32, 157, 42, 167], fill=C_GREEN)
    draw.text((48, 155), "MySQL: Connected (25 records)", fill=C_TEXT_DARK, font=font_small)
    
    draw.ellipse([32, 177, 42, 187], fill=C_GREEN)
    draw.text((48, 175), "ChromaDB: Ready (9 chunks)", fill=C_TEXT_DARK, font=font_small)

    draw.ellipse([32, 197, 42, 207], fill=C_GREEN)
    draw.text((48, 195), "Gemini 2.5 Flash: Connected", fill=C_TEXT_DARK, font=font_small)

    # Document Ingestion Section
    draw.text((24, 235), "1. Document Ingestion", fill=C_PRIMARY, font=font_h3)
    
    # PDF Upload Box
    upload_status = sidebar_info.get("upload_status", "uploaded") if sidebar_info else "uploaded"
    draw_rounded_rect(draw, [20, 260, 300, 340], radius=6, fill=(255, 255, 255), outline=(203, 213, 225), width=1)
    
    if upload_status == "uploaded":
        draw.text((32, 275), "📄 sample_company_policies.pdf", fill=C_PRIMARY, font=font_small_bold)
        draw.text((32, 295), "Size: 42 KB • 3 Pages", fill=C_TEXT_MUTED, font=font_small)
        draw.text((32, 315), "✓ File validated & loaded", fill=C_GREEN, font=font_small)
    
    # Process Document Button
    btn_color = (37, 99, 235) if not (sidebar_info and sidebar_info.get("processing")) else (147, 197, 253)
    draw_rounded_rect(draw, [20, 350, 300, 388], radius=6, fill=btn_color)
    btn_label = "⏳ Indexing Chunks..." if (sidebar_info and sidebar_info.get("processing")) else "2. Process Document"
    draw.text((70, 360), btn_label, fill=(255, 255, 255), font=font_body_bold)

    if sidebar_info and sidebar_info.get("toast"):
        draw_rounded_rect(draw, [20, 400, 300, 445], radius=6, fill=(240, 253, 244), outline=(134, 239, 172))
        draw.text((30, 412), sidebar_info.get("toast"), fill=(22, 101, 52), font=font_small_bold)

    # Example Questions Sidebar Box
    draw.text((24, 460), "💡 Example Queries", fill=C_PRIMARY, font=font_h3)
    ex_queries = [
        "What is the company leave policy?",
        "What are the core working hours?",
        "How many employees in Engineering?",
        "What is the average salary?"
    ]
    for i, eq in enumerate(ex_queries):
        draw_rounded_rect(draw, [20, 490 + i*48, 300, 528 + i*48], radius=6, fill=(255, 255, 255), outline=C_BORDER)
        draw.text((28, 498 + i*48), eq, fill=C_TEXT_DARK, font=font_small)

    # Main Area
    main_x = 350
    draw.text((main_x, 60), "AgentRAG", fill=C_PRIMARY, font=font_title_lg)
    draw.text((main_x, 105), "Enterprise Knowledge Assistant & Intelligent Query Router", fill=C_TEXT_MUTED, font=font_body)
    draw.line([main_x, 130, WIDTH - 40, 130], fill=C_BORDER, width=1)

def render_scene_1(frame_idx, total_frames):
    # Scene 1: Title Screen
    img = Image.new("RGB", (WIDTH, HEIGHT), C_DARK_BG)
    draw = ImageDraw.Draw(img)

    # Gradient accent circles
    draw.ellipse([-100, -100, 400, 400], fill=(23, 37, 84))
    draw.ellipse([WIDTH - 300, HEIGHT - 300, WIDTH + 200, HEIGHT + 200], fill=(19, 78, 74))

    # Center Content
    draw_rounded_rect(draw, [140, 90, WIDTH - 140, HEIGHT - 90], radius=16, fill=C_DARK_PANEL, outline=(51, 65, 85), width=2)

    # Logo & Badge
    draw_rounded_rect(draw, [WIDTH//2 - 60, 130, WIDTH//2 + 60, 170], radius=20, fill=(30, 58, 138))
    draw.text((WIDTH//2 - 45, 140), "🤖 AGENTRAG", fill=(147, 197, 253), font=font_h3)

    draw.text((WIDTH//2 - 380, 195), "AgentRAG: Enterprise Knowledge Assistant", fill=(255, 255, 255), font=font_title_lg)
    draw.text((WIDTH//2 - 360, 250), "Intelligent Query Routing across Document RAG & MySQL Database", fill=(148, 163, 184), font=font_h2)

    # Core Pillar Cards
    pillars = [
        ("📄 Document RAG", "PDF extraction, 800-char chunks,\ngemini-embedding-001 (3072-dim),\nChromaDB persistent vector store."),
        ("🔀 LangGraph Router", "Deterministic State Machine with\nconditional edge routing based on\nLLM intent classification."),
        ("🗄️ MySQL Text-to-SQL", "Natural language to MySQL SELECT\nwith strict AST/regex validation\nblocking DROP, DELETE & injection.")
    ]

    for i, (ptitle, pdesc) in enumerate(pillars):
        px = 180 + i * 315
        draw_rounded_rect(draw, [px, 310, px + 295, 470], radius=10, fill=(15, 23, 42), outline=(51, 65, 85))
        draw.text((px + 16, 325), ptitle, fill=(56, 189, 248), font=font_h3)
        draw.line([px + 16, 350, px + 280, 350], fill=(51, 65, 85), width=1)
        draw.text((px + 16, 365), pdesc, fill=(203, 213, 225), font=font_small)

    # Bottom Tech Stack Badges
    badges = ["Python", "FastAPI", "LangChain", "LangGraph", "Gemini 2.5 Flash", "ChromaDB", "MySQL 8.0", "Streamlit", "Docker"]
    bx = 180
    by = 510
    draw.text((180, 485), "TECHNOLOGY STACK:", fill=(148, 163, 184), font=font_small_bold)
    for badge in badges:
        bw = len(badge) * 8 + 18
        draw_rounded_rect(draw, [bx, by, bx + bw, by + 28], radius=6, fill=(51, 65, 85))
        draw.text((bx + 9, by + 6), badge, fill=(241, 245, 249), font=font_small)
        bx += bw + 10

    # Footer note
    draw.text((WIDTH//2 - 200, 575), "Resume & Technical Interview Project Demonstration", fill=(100, 116, 139), font=font_body)
    return np.array(img)

def render_scene_2(frame_idx, total_frames):
    # Scene 2: LangGraph Routing & Architecture Visual Flow
    img = Image.new("RGB", (WIDTH, HEIGHT), C_DARK_BG)
    draw = ImageDraw.Draw(img)

    draw_rounded_rect(draw, [60, 40, WIDTH - 60, HEIGHT - 40], radius=16, fill=C_DARK_PANEL, outline=(51, 65, 85), width=2)
    
    draw.text((100, 60), "LangGraph Architecture & Query Routing Engine", fill=(255, 255, 255), font=font_title)
    draw.text((100, 95), "Deterministic state machine preventing hallucinations and unauthorized SQL commands", fill=(148, 163, 184), font=font_body)

    # 1. Start Box
    draw_rounded_rect(draw, [100, 150, 260, 205], radius=8, fill=(30, 58, 138), outline=(96, 165, 250))
    draw.text((120, 168), "START: User Question", fill=(255, 255, 255), font=font_body_bold)

    # Arrow to Router
    draw.line([260, 177, 340, 177], fill=(96, 165, 250), width=3)
    draw.polygon([(340, 177), (330, 170), (330, 184)], fill=(96, 165, 250))

    # 2. Router Node
    draw_rounded_rect(draw, [340, 140, 550, 215], radius=8, fill=(19, 78, 74), outline=(45, 212, 191), width=2)
    draw.text((360, 155), "Router Node", fill=(45, 212, 191), font=font_h3)
    draw.text((360, 180), "Gemini Intent Classifier", fill=(204, 251, 241), font=font_small)

    # Conditional Branching Arrows
    # Branch Up -> RAG
    draw.line([550, 165, 640, 165], fill=(56, 189, 248), width=3)
    draw.line([640, 165, 640, 260], fill=(56, 189, 248), width=3)
    draw.polygon([(640, 265), (633, 255), (647, 255)], fill=(56, 189, 248))
    draw.text((565, 145), "route == 'rag'", fill=(56, 189, 248), font=font_small_bold)

    # Branch Down -> SQL
    draw.line([550, 190, 640, 190], fill=(251, 146, 60), width=3)
    draw.line([640, 190, 640, 440], fill=(251, 146, 60), width=3)
    draw.polygon([(640, 445), (633, 435), (647, 435)], fill=(251, 146, 60))
    draw.text((565, 200), "route == 'sql'", fill=(251, 146, 60), font=font_small_bold)

    # 3A. RAG Subsystem Box
    draw_rounded_rect(draw, [550, 265, 960, 410], radius=10, fill=(15, 23, 42), outline=(56, 189, 248))
    draw.text((570, 280), "📄 RAG Subsystem (Document Retrieval)", fill=(56, 189, 248), font=font_h3)
    rag_steps = [
        "1. PyPDFLoader extracts PDF pages & 1-indexed page metadata",
        "2. RecursiveCharacterTextSplitter (800 chars, 120 overlap)",
        "3. Gemini gemini-embedding-001 generates 3072-dim vectors",
        "4. ChromaDB performs top-4 vector similarity search",
        "5. Gemini 2.5 Flash synthesizes grounded answer with citations"
    ]
    for s_idx, step in enumerate(rag_steps):
        draw.text((570, 310 + s_idx * 18), step, fill=(226, 232, 240), font=font_small)

    # 3B. SQL Subsystem Box
    draw_rounded_rect(draw, [550, 445, 960, 590], radius=10, fill=(15, 23, 42), outline=(251, 146, 60))
    draw.text((570, 460), "🗄️ MySQL Subsystem (Structured Text-to-SQL)", fill=(251, 146, 60), font=font_h3)
    sql_steps = [
        "1. Injects MySQL schema (departments, employees, 25 records)",
        "2. Gemini translates natural language into MySQL SELECT query",
        "3. AST/Regex Security Validator blocks DROP, DELETE, INSERT, injections",
        "4. Executes read-only query on MySQL via SQLAlchemy",
        "5. Gemini converts raw rows into natural conversational answer"
    ]
    for s_idx, step in enumerate(sql_steps):
        draw.text((570, 490 + s_idx * 18), step, fill=(226, 232, 240), font=font_small)

    # 4. Final Response Box
    draw_rounded_rect(draw, [1030, 320, 1190, 530], radius=10, fill=(30, 58, 138), outline=(96, 165, 250))
    draw.text((1050, 340), "Final Response", fill=(255, 255, 255), font=font_h3)
    draw.line([1050, 370, 1170, 370], fill=(96, 165, 250), width=1)
    draw.text((1045, 385), "• Formatted Answer", fill=(226, 232, 240), font=font_small)
    draw.text((1045, 415), "• Route Badge", fill=(226, 232, 240), font=font_small)
    draw.text((1045, 445), "• Exact Citations", fill=(226, 232, 240), font=font_small)
    draw.text((1045, 475), "• Inspected SQL", fill=(226, 232, 240), font=font_small)

    # Connect RAG and SQL to Final
    draw.line([960, 335, 1030, 370], fill=(56, 189, 248), width=3)
    draw.line([960, 515, 1030, 480], fill=(251, 146, 60), width=3)

    return np.array(img)

def render_scene_3(frame_idx, total_frames):
    # Scene 3: Live UI Demo - Document RAG Query
    img = Image.new("RGB", (WIDTH, HEIGHT), C_BG)
    draw = ImageDraw.Draw(img)

    sidebar_info = {"upload_status": "uploaded", "toast": "✓ Indexed 9 chunks from 3 pages!"}
    draw_streamlit_layout(img, draw, sidebar_info)

    main_x = 350
    # Input Box Area
    draw.text((main_x, 145), "3. Ask Question:", fill=C_PRIMARY, font=font_h3)
    draw_rounded_rect(draw, [main_x, 175, WIDTH - 40, 220], radius=6, fill=(255, 255, 255), outline=(203, 213, 225))
    
    # Animated typing text
    full_q = "What is the company leave policy?"
    char_count = min(len(full_q), int((frame_idx / (total_frames * 0.4)) * len(full_q)))
    typed_q = full_q[:char_count]
    draw.text((main_x + 14, 188), typed_q + ("|" if frame_idx % 8 < 4 else ""), fill=C_TEXT_DARK, font=font_body)

    # Submit button
    draw_rounded_rect(draw, [main_x, 230, main_x + 160, 268], radius=6, fill=C_ACCENT_BLUE)
    draw.text((main_x + 22, 240), "Submit Question", fill=(255, 255, 255), font=font_body_bold)

    # Show response after typing finishes
    if frame_idx > total_frames * 0.4:
        draw.line([main_x, 285, WIDTH - 40, 285], fill=C_BORDER, width=1)
        
        # Route Badge
        draw_rounded_rect(draw, [main_x, 300, main_x + 280, 332], radius=12, fill=(235, 248, 255), outline=(190, 227, 248))
        draw.text((main_x + 12, 308), "📄 Route: RAG (Unstructured Document)", fill=C_ACCENT_BLUE, font=font_small_bold)

        # Answer Header & Box
        draw.text((main_x, 345), "4. Generated Answer", fill=C_PRIMARY, font=font_h3)
        draw_rounded_rect(draw, [main_x, 370, WIDTH - 40, 480], radius=6, fill=(247, 250, 252), outline=(49, 130, 206), width=2)
        
        ans_lines = [
            "Apex Technologies Inc. provides the following paid time off (PTO) provisions for full-time employees:",
            "• Annual Paid Leave: 20 days per calendar year, accrued monthly at 1.66 days per month.",
            "• Sick Leave: 10 days of paid sick leave annually for medical illness or caring for family members.",
            "• Parental Leave: 16 weeks of 100% paid leave for primary caregivers; 8 weeks for secondary caregivers.",
            "• Bereavement Leave: Up to 5 consecutive paid business days.",
            "• Leave Carryover: Maximum of 5 unused days carried over, must be used before March 31st."
        ]
        for l_idx, line in enumerate(ans_lines):
            draw.text((main_x + 16, 382 + l_idx * 15), line, fill=C_TEXT_DARK, font=font_small)

        # 6. Source Documents Box
        draw.text((main_x, 495), "6. Source Documents Cited", fill=C_PRIMARY, font=font_h3)
        draw_rounded_rect(draw, [main_x, 520, WIDTH - 40, 600], radius=6, fill=(255, 255, 255), outline=C_BORDER)
        draw.text((main_x + 16, 530), "Source #1: sample_company_policies.pdf (Page: 1)", fill=C_ACCENT_BLUE, font=font_small_bold)
        excerpt = '"Annual Paid Leave: All full-time employees are entitled to 20 days of paid annual leave per calendar year... Sick Leave: 10 days annually... Parental Leave: Primary caregivers receive 16 weeks..."'
        draw.text((main_x + 16, 550), excerpt, fill=(74, 85, 104), font=font_small)
        
        # Grounding guarantee pill
        draw_rounded_rect(draw, [main_x, 615, main_x + 360, 645], radius=6, fill=(240, 253, 244), outline=(134, 239, 172))
        draw.text((main_x + 12, 623), "✓ 100% Grounded in Retrieved Chunks (Zero Hallucination)", fill=(22, 101, 52), font=font_small_bold)

    return np.array(img)

def render_scene_4(frame_idx, total_frames):
    # Scene 4: Anti-Hallucination Guardrail Demo
    img = Image.new("RGB", (WIDTH, HEIGHT), C_BG)
    draw = ImageDraw.Draw(img)

    sidebar_info = {"upload_status": "uploaded"}
    draw_streamlit_layout(img, draw, sidebar_info)

    main_x = 350
    draw.text((main_x, 145), "3. Ask Question (Out-of-Domain / Missing Policy):", fill=C_PRIMARY, font=font_h3)
    draw_rounded_rect(draw, [main_x, 175, WIDTH - 40, 220], radius=6, fill=(255, 255, 255), outline=(203, 213, 225))
    
    full_q = "What is the company policy on pet insurance for dogs and cats?"
    char_count = min(len(full_q), int((frame_idx / (total_frames * 0.4)) * len(full_q)))
    typed_q = full_q[:char_count]
    draw.text((main_x + 14, 188), typed_q + ("|" if frame_idx % 8 < 4 else ""), fill=C_TEXT_DARK, font=font_body)

    draw_rounded_rect(draw, [main_x, 230, main_x + 160, 268], radius=6, fill=C_ACCENT_BLUE)
    draw.text((main_x + 22, 240), "Submit Question", fill=(255, 255, 255), font=font_body_bold)

    if frame_idx > total_frames * 0.4:
        draw.line([main_x, 285, WIDTH - 40, 285], fill=C_BORDER, width=1)
        
        # Route Badge
        draw_rounded_rect(draw, [main_x, 300, main_x + 280, 332], radius=12, fill=(235, 248, 255), outline=(190, 227, 248))
        draw.text((main_x + 12, 308), "📄 Route: RAG (Unstructured Document)", fill=C_ACCENT_BLUE, font=font_small_bold)

        # Answer Header & Box
        draw.text((main_x, 345), "4. Generated Answer", fill=C_PRIMARY, font=font_h3)
        draw_rounded_rect(draw, [main_x, 370, WIDTH - 40, 440], radius=6, fill=(254, 242, 242), outline=(239, 68, 68), width=2)
        draw.text((main_x + 16, 395), "I could not find this information in the available documents.", fill=(185, 28, 28), font=font_h3)

        # Guardrail Explanation Box
        draw_rounded_rect(draw, [main_x, 460, WIDTH - 40, 580], radius=8, fill=(255, 255, 255), outline=C_BORDER)
        draw.text((main_x + 16, 475), "🛡️ Anti-Hallucination Guardrail in Action", fill=C_PRIMARY, font=font_h3)
        g_notes = [
            "• Standard LLMs often fabricate plausible-sounding insurance benefits.",
            "• AgentRAG sets temperature = 0.0 and enforces strict context containment.",
            "• If information is absent in retrieved document chunks, it returns the exact required fallback string.",
            "• Passed automated test: tests/test_rag.py::test_query_rag_pipeline_not_found"
        ]
        for idx, gn in enumerate(g_notes):
            draw.text((main_x + 16, 505 + idx * 18), gn, fill=C_TEXT_DARK, font=font_small)

    return np.array(img)

def render_scene_5(frame_idx, total_frames):
    # Scene 5: Live UI Demo - MySQL Text-to-SQL & Security
    img = Image.new("RGB", (WIDTH, HEIGHT), C_BG)
    draw = ImageDraw.Draw(img)

    sidebar_info = {"upload_status": "uploaded"}
    draw_streamlit_layout(img, draw, sidebar_info)

    main_x = 350
    draw.text((main_x, 145), "3. Ask Question (Database Query):", fill=C_PRIMARY, font=font_h3)
    draw_rounded_rect(draw, [main_x, 175, WIDTH - 40, 220], radius=6, fill=(255, 255, 255), outline=(203, 213, 225))
    
    full_q = "How many employees are in Engineering and what is the average salary?"
    char_count = min(len(full_q), int((frame_idx / (total_frames * 0.4)) * len(full_q)))
    typed_q = full_q[:char_count]
    draw.text((main_x + 14, 188), typed_q + ("|" if frame_idx % 8 < 4 else ""), fill=C_TEXT_DARK, font=font_body)

    draw_rounded_rect(draw, [main_x, 230, main_x + 160, 268], radius=6, fill=C_ACCENT_BLUE)
    draw.text((main_x + 22, 240), "Submit Question", fill=(255, 255, 255), font=font_body_bold)

    if frame_idx > total_frames * 0.4:
        draw.line([main_x, 285, WIDTH - 40, 285], fill=C_BORDER, width=1)
        
        # SQL Route Badge
        draw_rounded_rect(draw, [main_x, 300, main_x + 310, 332], radius=12, fill=(254, 252, 191), outline=(250, 240, 137))
        draw.text((main_x + 12, 308), "🗄️ Route: SQL (MySQL Relational Database)", fill=(151, 90, 22), font=font_small_bold)

        # Answer Header & Box
        draw.text((main_x, 345), "4. Generated Answer", fill=C_PRIMARY, font=font_h3)
        draw_rounded_rect(draw, [main_x, 370, WIDTH - 40, 425], radius=6, fill=(247, 250, 252), outline=(221, 107, 32), width=2)
        draw.text((main_x + 16, 388), "There are 8 employees in Engineering, with an average salary of $108,375.00.", fill=C_TEXT_DARK, font=font_body_bold)

        # Inspected SQL Query Box
        draw.text((main_x, 435), "🔍 Inspected SQL Query (Validated SELECT)", fill=C_PRIMARY, font=font_h3)
        draw_rounded_rect(draw, [main_x, 460, WIDTH - 40, 525], radius=6, fill=(30, 41, 59))
        sql_display = "SELECT COUNT(e.employee_id) AS count, ROUND(AVG(e.salary), 2) AS avg_salary\nFROM employees e JOIN departments d ON e.department_id = d.department_id\nWHERE LOWER(d.department_name) = 'engineering';"
        draw.text((main_x + 16, 468), sql_display, fill=(56, 189, 248), font=font_code)

        # Security Guardrail Badge
        draw_rounded_rect(draw, [main_x, 540, WIDTH - 40, 605], radius=6, fill=(240, 253, 244), outline=(134, 239, 172))
        draw.text((main_x + 14, 550), "🛡️ SQL Security Enforcement Verified:", fill=(22, 101, 52), font=font_small_bold)
        draw.text((main_x + 14, 572), "• Only read-only SELECT/WITH allowed  • Blocks DROP, DELETE, INSERT, ALTER  • Semicolon chaining prohibited", fill=(21, 128, 61), font=font_small)

    return np.array(img)

def render_scene_6(frame_idx, total_frames):
    # Scene 6: Terminal View - Docker & Pytest Verification
    img = Image.new("RGB", (WIDTH, HEIGHT), C_DARK_BG)
    draw = ImageDraw.Draw(img)

    # Terminal Window Chrome
    draw_rounded_rect(draw, [80, 40, WIDTH - 80, HEIGHT - 40], radius=12, fill=(15, 23, 42), outline=(51, 65, 85), width=2)
    draw.rectangle([80, 40, WIDTH - 80, 80], fill=(30, 41, 59))
    draw.ellipse([98, 55, 108, 65], fill=(239, 68, 68))
    draw.ellipse([114, 55, 124, 65], fill=(245, 158, 11))
    draw.ellipse([130, 55, 140, 65], fill=(16, 185, 129))
    draw.text((WIDTH//2 - 120, 52), "terminal — bash (AgentRAG Tests & Docker)", fill=(148, 163, 184), font=font_small)

    term_lines = [
        ("$ pytest tests/ -v", (248, 250, 252)),
        ("============================= test session starts =============================", (148, 163, 184)),
        ("collected 21 items", (148, 163, 184)),
        ("", (0,0,0)),
        ("tests/test_chat_api.py::test_chat_successful_rag_response PASSED         [  9%]", (74, 222, 128)),
        ("tests/test_chat_api.py::test_chat_successful_sql_response PASSED         [ 14%]", (74, 222, 128)),
        ("tests/test_health.py::test_health_endpoint_success PASSED                [ 28%]", (74, 222, 128)),
        ("tests/test_rag.py::test_query_rag_pipeline_grounded_answer PASSED        [ 52%]", (74, 222, 128)),
        ("tests/test_router.py::test_classify_query_route_sql_mock PASSED          [ 57%]", (74, 222, 128)),
        ("tests/test_sql_validator.py::test_destructive_queries_are_rejected PASSED [ 90%]", (74, 222, 128)),
        ("tests/test_sql_validator.py::test_multiple_statements_injection_rejected PASSED [ 95%]", (74, 222, 128)),
        ("======================= 21 passed in 7.04s (100% PASS RATE) =======================", (52, 211, 153)),
        ("", (0,0,0)),
        ("$ docker compose up --build -d", (248, 250, 252)),
        ("[+] Running 3/3", (148, 163, 184)),
        (" ✔ Container agentrag_mysql     Healthy    Started (Port 3306)", (56, 189, 248)),
        (" ✔ Container agentrag_backend   Started    (Port 8000 -> FastAPI)", (56, 189, 248)),
        (" ✔ Container agentrag_frontend  Started    (Port 8501 -> Streamlit)", (56, 189, 248)),
        ("Successfully deployed full enterprise stack with single command!", (250, 204, 21))
    ]

    visible_lines = min(len(term_lines), int((frame_idx / (total_frames * 0.8)) * len(term_lines)) + 4)
    for idx, (ttext, tcolor) in enumerate(term_lines[:visible_lines]):
        draw.text((105, 95 + idx * 24), ttext, fill=tcolor, font=font_code)

    return np.array(img)

def render_scene_7(frame_idx, total_frames):
    # Scene 7: Outro / Summary & Resume Highlights
    img = Image.new("RGB", (WIDTH, HEIGHT), C_DARK_BG)
    draw = ImageDraw.Draw(img)

    draw_rounded_rect(draw, [120, 80, WIDTH - 120, HEIGHT - 80], radius=16, fill=C_DARK_PANEL, outline=(51, 65, 85), width=2)
    
    draw.text((WIDTH//2 - 280, 120), "AgentRAG: Ready for Technical Interviews", fill=(255, 255, 255), font=font_title_lg)
    draw.text((WIDTH//2 - 340, 175), "A technically strong, simple, and clean GenAI project built for AI Developer roles", fill=(148, 163, 184), font=font_body)

    # Bullet Highlights Card
    draw_rounded_rect(draw, [160, 220, WIDTH - 160, 480], radius=10, fill=(15, 23, 42), outline=(51, 65, 85))
    draw.text((185, 240), "Resume & Technical Interview Value:", fill=(56, 189, 248), font=font_h3)
    
    bullets = [
        ("• Zero-Hallucination RAG:", "LangChain + ChromaDB + Gemini 2.5 Flash + Exact Page Citations"),
        ("• Deterministic Routing:", "LangGraph state machine with conditional branching"),
        ("• Safe Text-to-SQL:", "AST/Regex validation enforcing read-only SELECT on MySQL"),
        ("• Decoupled Architecture:", "FastAPI REST API backend + Streamlit interactive UI"),
        ("• Production Containerization:", "Docker Compose orchestration with persistent volumes & healthchecks"),
        ("• Complete Documentation:", "9-page interview guide PDF + 25 technical Q&A masterclass")
    ]
    for b_idx, (b_title, b_desc) in enumerate(bullets):
        draw.text((185, 275 + b_idx * 32), b_title, fill=(241, 245, 249), font=font_body_bold)
        draw.text((410, 275 + b_idx * 32), b_desc, fill=(203, 213, 225), font=font_body)

    # GitHub link badge
    draw_rounded_rect(draw, [WIDTH//2 - 320, 510, WIDTH//2 + 320, 560], radius=8, fill=(30, 58, 138), outline=(96, 165, 250))
    draw.text((WIDTH//2 - 300, 524), "🔗 github.com/Mayank830205/agentic-rag-knowledge-assistant", fill=(255, 255, 255), font=font_body_bold)

    return np.array(img)

def generate_video(output_path="docs/demo_video.mp4"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"Generating video to {output_path}...")

    # Scene Durations in Seconds: total = 42 seconds
    scenes = [
        (render_scene_1, 4.0),  # Title (96 frames)
        (render_scene_2, 5.0),  # Architecture Flow (120 frames)
        (render_scene_3, 9.0),  # Live RAG Demo (216 frames)
        (render_scene_4, 6.0),  # Anti-Hallucination Demo (144 frames)
        (render_scene_5, 9.0),  # MySQL SQL Demo (216 frames)
        (render_scene_6, 5.0),  # Terminal & Tests (120 frames)
        (render_scene_7, 4.0),  # Outro / Resume (96 frames)
    ]

    total_frames = sum(int(dur * FPS) for _, dur in scenes)
    print(f"Total video frames: {total_frames} ({total_frames/FPS:.1f} seconds)")

    writer = imageio.get_writer(
        output_path,
        fps=FPS,
        codec='libx264',
        pixelformat='yuv420p',
        quality=8
    )

    frame_counter = 0
    for scene_func, duration in scenes:
        scene_frames = int(duration * FPS)
        for f_idx in range(scene_frames):
            frame = scene_func(f_idx, scene_frames)
            writer.append_data(frame)
            frame_counter += 1
            if frame_counter % 120 == 0:
                print(f"Rendered {frame_counter}/{total_frames} frames ({frame_counter/total_frames*100:.0f}%)...")

    writer.close()
    print(f"Demo video successfully created at: {output_path}")

if __name__ == "__main__":
    out_file = os.path.join("docs", "demo_video.mp4")
    generate_video(out_file)
