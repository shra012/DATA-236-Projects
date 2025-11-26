import base64
import html
import io
import json
import re
import time
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple

import requests
import streamlit as st
import streamlit.components.v1 as components
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fpdf import FPDF
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.units import inch

from career_counselor_agent import tools as cc_tools
from career_counselor_agent.agent import DEFAULT_SYSTEM_PROMPT, build_agent_executor, build_llm, build_memory

load_dotenv()
st.set_page_config(page_title="Career Counseling Agent", page_icon=None, layout="wide")

PAGES = ["Skills Gap Analyzer", "Resume Scorer", "Salary Estimator", "Interview Questions", "Chat Agent"]
ERROR_RESPONSE = {
    "overall_score": 0,
    "score_breakdown": {
        "formatting_and_structure": {"score": 0, "comment": "Error occurred"},
        "clarity_and_impact": {"score": 0, "comment": "Error occurred"},
        "skills_and_keywords_match": {"score": 0, "comment": "Error occurred"},
        "quantification_and_results": {"score": 0, "comment": "Error occurred"}
    },
    "summary_feedback": {"top_strengths": [], "top_issues": [], "overall_comment": ""},
    "improvement_suggestions": [],
    "improved_resume_text": "",
    "diff_html": ""
}


def theme_css() -> str:
    bg, card_bg, card_border, text, accent = "#0f172a", "#1e293b", "#334155", "#f1f5f9", "#3b82f6"
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600&display=swap');
    html, body, [class*="css"] {{ color: {text}; font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif; }}
    .main {{ background: radial-gradient(circle at 20% 20%, rgba(59,130,246,0.08), transparent 35%), radial-gradient(circle at 80% 0%, rgba(16,185,129,0.08), transparent 25%), {bg}; }}
    .resume-diff {{ background: {card_bg}; padding: 15px; border-radius: 8px; line-height: 1.8; }}
    .context-card {{ background: {card_bg}; border: 1px solid {card_border}; padding: 15px; border-radius: 8px; margin: 15px 0; }}
    .insight-bad {{ background: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.4); color: #fecdd3; padding: 10px 12px; border-radius: 10px; margin-bottom: 8px; }}
    .insight-good {{ background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.4); color: #bbf7d0; padding: 10px 12px; border-radius: 10px; margin-bottom: 8px; }}
    [data-testid="stTextInputInstructions"], [data-testid="stNumberInputInstructions"], [data-testid="stTextInputInstructions"] *, [data-testid="stNumberInputInstructions"] * {{ display: none !important; }}
    [data-testid="stChatInputInstructions"], [data-testid="stChatInputHelper"] {{ display: none !important; }}
    [data-testid="stSidebar"] {{ background: {card_bg} !important; border-left: 1px solid {card_border} !important; }}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"], [data-testid="stSidebar"] * {{ color: {text} !important; }}
    </style>
    """


def apply_theme() -> None:
    st.markdown(theme_css(), unsafe_allow_html=True)


def extract_resume_text(uploaded_file) -> Tuple[Optional[str], Optional[bytes], Optional[str]]:
    if not uploaded_file:
        return None, None, "Upload a resume to proceed."
    try:
        bytes_data = uploaded_file.read()
        uploaded_file.seek(0)
        if uploaded_file.name.lower().endswith(".pdf"):
            text = "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(bytes_data)).pages)
        else:
            text = bytes_data.decode("utf-8", errors="ignore")
        return "\n".join(line.strip() for line in text.splitlines() if line.strip()), bytes_data, None
    except Exception as e:
        return None, None, f"Could not read file: {e}"


def scrape_job_description(url: str) -> Tuple[Optional[str], Optional[str]]:
    if not url:
        return None, "Provide a job link to scrape."
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        return " ".join(soup.get_text(separator=" ").split())[:6000], None
    except Exception as e:
        return None, f"Failed to scrape: {e}"


def format_skills(skills: set[str]) -> str:
    return ", ".join(sorted(skills)) if skills else "None detected"


def highlight_diff_lines(old_text: str, new_text: str) -> Tuple[str, List[str]]:
    old_lines, new_lines = old_text.splitlines(), new_text.splitlines()
    sm = SequenceMatcher(None, old_lines, new_lines)
    html_lines, changes = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            html_lines.extend(html.escape(line) for line in new_lines[j1:j2])
        elif tag == "insert":
            for line in new_lines[j1:j2]:
                html_lines.append(f"<span style='background:rgba(34,197,94,0.18);color:#4ade80;'>{html.escape(line)}</span>")
                if line.strip():
                    changes.append(f"Added: {line.strip()}")
        elif tag == "delete":
            for line in old_lines[i1:i2]:
                html_lines.append(f"<span style='text-decoration:line-through;color:#f87171;'>{html.escape(line)}</span>")
                if line.strip():
                    changes.append(f"Removed: {line.strip()}")
        elif tag == "replace":
            for old_line, new_line in zip(old_lines[i1:i2], new_lines[j1:j2]):
                old_tokens, new_tokens = old_line.split(), new_line.split()
                sm_inline = SequenceMatcher(None, old_tokens, new_tokens)
                parts = []
                for t, o1, o2, n1, n2 in sm_inline.get_opcodes():
                    old_chunk = " ".join(old_tokens[o1:o2])
                    new_chunk = " ".join(new_tokens[n1:n2])
                    if t == "equal":
                        parts.append(new_chunk)
                    elif t == "insert":
                        parts.append(f"<span style='background:rgba(16,185,129,0.25);color:#bbf7d0;'>{new_chunk}</span>")
                    elif t == "delete":
                        parts.append(f"<span style='text-decoration:line-through;color:#fca5a5;'>{old_chunk}</span>")
                    elif t == "replace":
                        parts.append(f"<span style='text-decoration:line-through;color:#fca5a5;'>{old_chunk}</span> <span style='background:rgba(16,185,129,0.25);color:#bbf7d0;'>{new_chunk}</span>")
                html_lines.append(" ".join(parts))
                changes.append(f"Updated: {old_line.strip()} -> {new_line.strip()}")
            if (i2 - i1) < (j2 - j1):
                for extra in new_lines[j1 + (i2 - i1):j2]:
                    html_lines.append(f"<span style='background:rgba(34,197,94,0.18);color:#4ade80;'>{html.escape(extra)}</span>")
                    if extra.strip():
                        changes.append(f"Added: {extra.strip()}")
            elif (i2 - i1) > (j2 - j1):
                for extra in old_lines[i1 + (j2 - j1):i2]:
                    html_lines.append(f"<span style='text-decoration:line-through;color:#f87171;'>{html.escape(extra)}</span>")
                    if extra.strip():
                        changes.append(f"Removed: {extra.strip()}")
    return "<br/>".join(html_lines), changes


def pdf_iframe(pdf_bytes: bytes, height: int = 500) -> None:
    b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    components.html(f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="{height}" type="application/pdf"></iframe>', height=height + 20, scrolling=True)


def analyze_resume_with_llm(resume_text: str, job_description: str = "", model: str = "gpt-5-nano", temperature: float = 0.3) -> Dict[str, Any]:
    if len(resume_text) > 10000:
        raise ValueError("Resume text too long. Limit to 10,000 characters.")
    jd_text = job_description or "(empty - no job description provided)"
    prompt = f"""You are an expert resume reviewer. Analyze the resume and provide feedback in the exact JSON format specified.

RESUME_TEXT:
{resume_text}

JOB_DESCRIPTION:
{jd_text}

Analyze this resume and return ONLY valid JSON (no markdown, no backticks, no explanations) with this exact structure:

{{
  "overall_score": 0-10,
  "score_breakdown": {{
    "formatting_and_structure": {{"score": 0-10, "comment": "short explanation"}},
    "clarity_and_impact": {{"score": 0-10, "comment": "short explanation"}},
    "skills_and_keywords_match": {{"score": 0-10, "comment": "short explanation, mention ATS/keywords and job match if JD is provided"}},
    "quantification_and_results": {{"score": 0-10, "comment": "short explanation, focus on metrics, achievements"}}
  }},
  "summary_feedback": {{
    "top_strengths": ["bullet point strength 1", "bullet point strength 2"],
    "top_issues": ["bullet point issue 1", "bullet point issue 2"],
    "overall_comment": "2-4 sentences summarising overall impression"
  }},
  "improvement_suggestions": [
    {{
      "section": "Section name",
      "issue": "What is wrong or can be improved",
      "suggestion": "Specific change or rewrite suggestion",
      "example_rewrite": "Concrete improved sentence or bullet"
    }}
  ],
  "improved_resume_text": "A fully improved resume, in plain text, preserving the original structure",
  "diff_html": "HTML string with <span style=\\"color:red;text-decoration:line-through;\\">deleted</span> and <span style=\\"color:green;\\">added</span> text"
}}

Remember:
- overall_score is holistic judgment, not average
- Be specific and actionable in feedback
- improved_resume_text should preserve structure but be stronger
- diff_html should show changes clearly with red strikethrough for deletions and green for additions
- Output ONLY valid JSON, nothing else"""

    try:
        valid_models = ["gpt-4o", "gpt-4", "gpt-3.5-turbo", "gpt-4-turbo", "gpt-5-nano", "gpt-5-mini"]
        if model not in valid_models:
            model = "gpt-4o"
        llm = build_llm(model=model, temperature=temperature)
        start_time = time.time()
        response_obj = llm.invoke(prompt)
        if not hasattr(response_obj, 'content'):
            raise ValueError("Invalid response format")
        response = response_obj.content.strip()
        if time.time() - start_time > 120:
            raise TimeoutError("Request exceeded 120 seconds")
        if not response or len(response) < 10:
            raise ValueError("Empty or invalid response")
        if response.startswith("```"):
            parts = response.split("```")
            if len(parts) > 1:
                response = parts[1]
                if response.startswith("json"):
                    response = response[4:]
                response = response.strip()
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            response = json_match.group(0)
        parsed = json.loads(response)
        if not isinstance(parsed, dict):
            raise ValueError("Response is not a valid JSON object")
        required_keys = ["overall_score", "score_breakdown", "summary_feedback", "improvement_suggestions", "improved_resume_text", "diff_html"]
        defaults = {"score_breakdown": {}, "improvement_suggestions": [], "improved_resume_text": "", "diff_html": "", "overall_score": 0, "summary_feedback": {"top_strengths": [], "top_issues": [], "overall_comment": ""}}
        for key in required_keys:
            if key not in parsed:
                parsed[key] = defaults.get(key, "" if isinstance(defaults.get(key), str) else [] if isinstance(defaults.get(key), list) else {})
        return parsed
    except json.JSONDecodeError as e:
        error_resp = ERROR_RESPONSE.copy()
        error_resp["summary_feedback"] = {"top_strengths": [], "top_issues": ["JSON parsing error"], "overall_comment": f"Unable to parse AI response: {str(e)[:200]}. Check API key."}
        error_resp["improved_resume_text"] = resume_text
        error_resp["diff_html"] = resume_text
        return error_resp
    except Exception as e:
        error_msg = str(e)[:200]
        error_resp = ERROR_RESPONSE.copy()
        error_resp["summary_feedback"] = {"top_strengths": [], "top_issues": ["Analysis error"], "overall_comment": f"Error: {error_msg}. Check API key and try again."}
        error_resp["improved_resume_text"] = resume_text
        error_resp["diff_html"] = resume_text
        return error_resp


def generate_pdf_from_text(text: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.set_font("Helvetica", size=11)
    max_width = pdf.w - 2 * pdf.l_margin - 2
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            pdf.ln(4)
            continue
        tokens = line.split(" ")
        safe_tokens = []
        for token in tokens:
            safe_tokens.extend([token[i:i+60] for i in range(0, len(token), 60)] if len(token) > 60 else [token])
        safe_line_ascii = " ".join(safe_tokens).encode("ascii", errors="replace").decode("ascii")
        try:
            pdf.multi_cell(max_width, 8, text=safe_line_ascii, align="L")
        except Exception:
            pdf.multi_cell(max_width, 8, text=safe_line_ascii[:200], align="L")
    output = pdf.output(dest="S")
    return bytes(output) if isinstance(output, (bytes, bytearray)) else str(output).encode("latin1", errors="ignore")


def create_annotated_pdf(original_text: str, improved_text: str, original_pdf_bytes: Optional[bytes] = None) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin, line_height = 0.75 * inch, 14
    y_position = height - margin
    original_lines, improved_lines = original_text.splitlines(), improved_text.splitlines()
    sm = SequenceMatcher(None, original_lines, improved_lines)
    c.setFont("Helvetica", 10)
    
    def new_page_if_needed():
        nonlocal y_position
        if y_position < margin + line_height:
            c.showPage()
            y_position = height - margin
    
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for line in improved_lines[j1:j2]:
                new_page_if_needed()
                c.setFillColor(colors.black)
                c.drawString(margin, y_position, line[:100])
                y_position -= line_height
        elif tag == "insert":
            for line in improved_lines[j1:j2]:
                new_page_if_needed()
                c.setFillColor(colors.HexColor("#22c55e"))
                c.setFillAlpha(0.3)
                c.rect(margin - 2, y_position - 2, width - 2 * margin + 4, line_height + 2, fill=1, stroke=0)
                c.setFillAlpha(1.0)
                c.setFillColor(colors.HexColor("#4ade80"))
                c.drawString(margin, y_position, f"+ {line[:95]}")
                y_position -= line_height
        elif tag == "delete":
            for line in original_lines[i1:i2]:
                new_page_if_needed()
                c.setFillColor(colors.HexColor("#f87171"))
                c.drawString(margin, y_position, f"- {line[:95]}")
                c.setStrokeColor(colors.HexColor("#f87171"))
                c.line(margin, y_position + 5, margin + stringWidth(line[:95], "Helvetica", 10), y_position + 5)
                y_position -= line_height
        elif tag == "replace":
            max_lines = max(i2 - i1, j2 - j1)
            for idx in range(max_lines):
                if y_position < margin + line_height * 2:
                    c.showPage()
                    y_position = height - margin
                if idx < (i2 - i1):
                    old_line = original_lines[i1 + idx]
                    c.setFillColor(colors.HexColor("#f87171"))
                    c.drawString(margin, y_position, f"- {old_line[:95]}")
                    c.setStrokeColor(colors.HexColor("#f87171"))
                    c.line(margin, y_position + 5, margin + stringWidth(old_line[:95], "Helvetica", 10), y_position + 5)
                    y_position -= line_height
                if idx < (j2 - j1):
                    new_line = improved_lines[j1 + idx]
                    c.setFillColor(colors.HexColor("#22c55e"))
                    c.setFillAlpha(0.3)
                    c.rect(margin - 2, y_position - 2, width - 2 * margin + 4, line_height + 2, fill=1, stroke=0)
                    c.setFillAlpha(1.0)
                    c.setFillColor(colors.HexColor("#4ade80"))
                    c.drawString(margin, y_position, f"+ {new_line[:95]}")
                    y_position -= line_height
    c.save()
    buffer.seek(0)
    return buffer.read()


def annotate_existing_pdf(original_pdf_bytes: bytes, original_text: str, improved_text: str) -> bytes:
    try:
        PdfReader(io.BytesIO(original_pdf_bytes))
        return create_annotated_pdf(original_text, improved_text, original_pdf_bytes)
    except Exception:
        return create_annotated_pdf(original_text, improved_text)


def init_state() -> None:
    defaults = {
        "messages": [], "memory": build_memory(), "agent": None,
        "tools": [cc_tools.skills_gap_analyzer, cc_tools.resume_scorer, cc_tools.salary_estimator, cc_tools.interview_question_generator],
        "config": {}, "improved_resume": None, "resume_bytes": None, "resume_original_text": None,
        "annotated_pdf_bytes": None, "menu_open": False, "current_page": "Skills Gap Analyzer",
        "resume_analysis": None, "job_description_text": ""
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_chat() -> None:
    st.session_state.messages = []
    st.session_state.memory.chat_memory.clear()


def build_config(form_values: Dict[str, Any]) -> Dict[str, Any]:
    model = form_values.get("model", "gpt-5-nano")
    return {
        "model": model,
        "temperature": 1.0 if model.startswith("gpt-5") else 0.3,
        "target_role": form_values.get("target_role", "").strip(),
        "location": form_values.get("location", "").strip(),
        "years_experience": form_values.get("years_experience", 3.0),
        "is_remote": form_values.get("is_remote", False),
    }


def ensure_agent(config: Dict[str, Any], show_toast: bool = False) -> bool:
    if st.session_state.config != config or st.session_state.agent is None:
        try:
            llm = build_llm(model=config["model"], temperature=float(config["temperature"]))
            contextual_prompt = f"{DEFAULT_SYSTEM_PROMPT}\nUser context: target role={config['target_role'] or 'unspecified'}; location={config['location'] or 'unspecified'}; experience={config['years_experience']} years; remote={config['is_remote']}."
            st.session_state.agent = build_agent_executor(llm=llm, tools=st.session_state.tools, memory=st.session_state.memory, system_prompt=contextual_prompt)
            st.session_state.config = config
            if show_toast:
                st.toast("Agent updated.", icon="check")
            return True
        except Exception as e:
            st.error(f"Failed to initialize agent. Check OPENAI_API_KEY: {str(e)}")
            return False
    if show_toast:
        st.toast("Agent up to date.", icon="info")
    return False


def render_navigation() -> None:
    cols = st.columns(5)
    page_names = ["Skills Gap", "Resume Scorer", "Salary", "Interview", "Chat"]
    for col, page_name, page_key in zip(cols, page_names, PAGES):
        with col:
            if st.button(page_name, use_container_width=True, type="primary" if st.session_state.current_page == page_key else "secondary"):
                st.session_state.current_page = page_key
                st.rerun()


init_state()
apply_theme()
render_navigation()

with st.sidebar:
    st.header("Configuration")
    model = st.selectbox("Model", options=["gpt-5-nano", "gpt-5-mini", "gpt-4o"], index=0)
    sidebar_target_role = st.text_input("Default target role", value="Data Scientist")
    sidebar_location = st.text_input("Default location", value="San Francisco, CA")
    sidebar_years_experience = st.number_input("Default years of experience", min_value=0.0, max_value=40.0, value=3.0, step=0.5)
    sidebar_is_remote = st.checkbox("Remote-friendly", value=True)
    submitted = st.button("Update chat agent", use_container_width=True)
    st.button("Start fresh chat", on_click=reset_chat, use_container_width=True, type="secondary")
    st.markdown("**Quick prompts**")
    st.caption("- Skills gap tab: Upload resume + job link, then analyze.\n- Salary tab: \"Estimate salary for remote ML Engineer in Seattle with 5 years.\"\n- Interview tab: \"Hard PM questions about product sense and metrics.\"")

config = build_config({"model": model, "target_role": sidebar_target_role, "location": sidebar_location, "years_experience": sidebar_years_experience, "is_remote": sidebar_is_remote})
if submitted:
    ensure_agent(config, show_toast=True)
if st.session_state.agent is None:
    ensure_agent(config)

if st.session_state.current_page == "Skills Gap Analyzer":
    st.title("Skills Gap Analyzer")
    st.markdown("Upload your resume and a job link; we scrape the description to compare skills and propose a learning path.")
    with st.form("skills_gap_form"):
        resume_file = st.file_uploader("Upload resume (PDF or text)", type=["pdf", "txt", "md"])
        manual_skills = st.text_area("Add/override skills (optional)", placeholder="Python, SQL, Tableau, ML, ...")
        job_url = st.text_input("Job link to scrape", placeholder="https://careers.example.com/job")
        job_desc = st.text_area("Or paste the job description", height=140)
        target_role_gap = st.text_input("Target role", value=sidebar_target_role)
        submitted_gap = st.form_submit_button("Analyze gap", use_container_width=True)

    if submitted_gap:
        resume_text, resume_bytes, resume_err = extract_resume_text(resume_file)
        if resume_err:
            st.error(resume_err)
        elif not job_url and not job_desc.strip():
            st.error("Provide a job link to scrape or paste the job description.")
        else:
            scraped_text, scrape_err = scrape_job_description(job_url) if job_url else (None, None)
            if scrape_err:
                st.warning(scrape_err)
            job_text = scraped_text or job_desc
            resume_skills = cc_tools._extract_skills_from_text(resume_text) if resume_text else set()
            user_skill_text = ", ".join(filter(None, [manual_skills.strip(), ", ".join(sorted(resume_skills)) if resume_skills else None])) or resume_text or "No skills provided."
            with st.spinner("Analyzing gap..."):
                result = cc_tools.skills_gap_analyzer.invoke({"user_skills": user_skill_text, "target_role": target_role_gap, "job_description": job_text})
            st.success("Skills gap analysis")
            st.markdown(f"```\n{result}\n```")
            col_a, col_b = st.columns(2)
            with col_a:
                st.caption("Detected skills in resume")
                st.code(format_skills(resume_skills))
            with col_b:
                st.caption("Detected skills in job description")
                st.code(format_skills(cc_tools._extract_skills_from_text(job_text or "") if job_text else set()))
            if job_text:
                with st.expander("Preview of scraped job description"):
                    st.write(job_text[:1200] + ("..." if len(job_text) > 1200 else ""))

elif st.session_state.current_page == "Resume Scorer":
    st.title("Resume Reviewer")
    st.markdown("Upload your resume to get a comprehensive 0-10 score, actionable feedback, and an improved version with visual diff.")
    with st.form("resume_score_form"):
        resume_file_score = st.file_uploader("Upload resume (PDF or text)", type=["pdf", "txt", "md"], key="resume_score_upload")
        fallback_text = st.text_area("Or paste resume text (used if no file or file cannot be read)", height=180, key="resume_fallback_text")
        job_description_text = st.text_area("Job description (optional)", height=120, placeholder="Paste the job description here for targeted feedback and keyword matching...", key="job_description_input")
        submitted_score = st.form_submit_button("Analyze Resume", use_container_width=True)

    if submitted_score:
        resume_text_score, resume_bytes_score, resume_err_score = extract_resume_text(resume_file_score)
        if resume_err_score and not fallback_text.strip():
            st.error(resume_err_score)
        else:
            payload_text = resume_text_score or fallback_text
            if not payload_text:
                st.error("Provide a resume file or paste the text to analyze.")
            else:
                if resume_bytes_score:
                    st.session_state.resume_bytes = resume_bytes_score
                st.session_state.resume_original_text = payload_text
                st.session_state.job_description_text = job_description_text.strip()
                try:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    status_text.text("Initializing AI analysis...")
                    progress_bar.progress(10)
                    status_text.text("Sending request to AI model...")
                    progress_bar.progress(30)
                    analysis_result = analyze_resume_with_llm(payload_text, job_description_text.strip(), model=config["model"], temperature=config["temperature"])
                    progress_bar.progress(90)
                    status_text.text("Processing results...")
                    st.session_state.resume_analysis = analysis_result
                    st.session_state.improved_resume = analysis_result.get("improved_resume_text", payload_text)
                    progress_bar.progress(100)
                    status_text.empty()
                    progress_bar.empty()
                    st.rerun()
                except TimeoutError as e:
                    st.error(f"Analysis timed out: {str(e)}. Try again with a shorter resume.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    if "API" in str(e) or "key" in str(e).lower():
                        st.info("Check your OPENAI_API_KEY in .env file.")
                    elif "model" in str(e).lower():
                        st.info(f"Model '{config['model']}' may not be available. Try 'gpt-4o'.")

    if "resume_analysis" in st.session_state and st.session_state.resume_analysis:
        analysis = st.session_state.resume_analysis
        st.markdown("---")
        col_score, col_breakdown = st.columns([1, 2])
        with col_score:
            score = analysis.get("overall_score", 0)
            st.metric("Overall Score", f"{score}/10")
            score_color = "#22c55e" if score >= 7 else "#f59e0b" if score >= 5 else "#ef4444"
            st.markdown(f"<div style='text-align:center;color:{score_color};font-size:14px;margin-top:10px;'>{'Excellent' if score >= 8 else 'Good' if score >= 6 else 'Needs Improvement' if score >= 4 else 'Poor'}</div>", unsafe_allow_html=True)
        with col_breakdown:
            st.markdown("**Score Breakdown**")
            for category, data in analysis.get("score_breakdown", {}).items():
                if isinstance(data, dict):
                    st.markdown(f"**{category.replace('_', ' ').title()}**: {data.get('score', 0)}/10 - {data.get('comment', '')}")
        st.markdown("---")
        summary = analysis.get("summary_feedback", {})
        col_strengths, col_issues = st.columns(2)
        with col_strengths:
            st.markdown("**Top Strengths**")
            strengths = summary.get("top_strengths", [])
            if strengths:
                for strength in strengths:
                    st.markdown(f"<div class='insight-good'>{strength}</div>", unsafe_allow_html=True)
            else:
                st.info("No specific strengths identified.")
        with col_issues:
            st.markdown("**Top Issues**")
            issues = summary.get("top_issues", [])
            if issues:
                for issue in issues:
                    st.markdown(f"<div class='insight-bad'>{issue}</div>", unsafe_allow_html=True)
            else:
                st.info("No major issues identified.")
        if summary.get("overall_comment"):
            st.markdown("**Overall Assessment**")
            st.info(summary.get("overall_comment"))
        suggestions = analysis.get("improvement_suggestions", [])
        if suggestions:
            st.markdown("---")
            st.markdown("**Improvement Suggestions**")
            for idx, suggestion in enumerate(suggestions, 1):
                with st.expander(f"{idx}. {suggestion.get('section', 'General')}"):
                    st.markdown(f"**Issue:** {suggestion.get('issue', '')}")
                    st.markdown(f"**Suggestion:** {suggestion.get('suggestion', '')}")
                    if suggestion.get('example_rewrite'):
                        st.markdown("**Example:**")
                        st.code(suggestion.get('example_rewrite'))
        if st.session_state.improved_resume:
            st.markdown("---")
            st.markdown("**Improved Resume**")
            diff_html = analysis.get("diff_html", "")
            if diff_html:
                st.markdown("**Visual Diff (Green = Added, Red Strikethrough = Removed)**")
                st.markdown(f"<div class='resume-diff'>{diff_html}</div>", unsafe_allow_html=True)
            with st.expander("View Full Improved Resume Text"):
                st.text_area("Improved Resume", st.session_state.improved_resume, height=400, key="improved_resume_display")
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button("Download Improved Resume (PDF)", data=generate_pdf_from_text(st.session_state.improved_resume), file_name="improved_resume.pdf", mime="application/pdf", use_container_width=True, key="download_improved_pdf")
            with col_dl2:
                if st.session_state.resume_bytes:
                    try:
                        annotated_pdf_bytes = annotate_existing_pdf(st.session_state.resume_bytes, st.session_state.resume_original_text, st.session_state.improved_resume)
                        st.download_button("Download Annotated Resume (PDF)", data=annotated_pdf_bytes, file_name="resume_with_edits.pdf", mime="application/pdf", use_container_width=True, key="download_annotated_pdf")
                    except Exception as e:
                        st.warning(f"Could not create annotated PDF: {e}")
        if st.session_state.resume_original_text:
            with st.expander("View Original Resume"):
                if st.session_state.resume_bytes:
                    pdf_iframe(st.session_state.resume_bytes, height=600)
                else:
                    st.text_area("Original Resume", st.session_state.resume_original_text, height=300, disabled=True)

elif st.session_state.current_page == "Salary Estimator":
    st.title("Salary Estimator")
    st.markdown("Get realistic salary ranges based on job title, location, and experience.")
    with st.form("salary_form"):
        job_title_sal = st.text_input("Job title", value=sidebar_target_role, key="salary_title")
        location_sal = st.text_input("Location", value=sidebar_location, key="salary_location")
        years_sal = st.number_input("Years of experience", min_value=0.0, max_value=40.0, value=sidebar_years_experience, step=0.5)
        is_remote_sal = st.checkbox("Remote-friendly", value=sidebar_is_remote, key="salary_remote")
        submitted_salary = st.form_submit_button("Estimate salary", use_container_width=True)
    if submitted_salary:
        with st.spinner("Estimating salary..."):
            result = cc_tools.salary_estimator.invoke({"job_title": job_title_sal, "location": location_sal, "years_experience": years_sal, "is_remote": is_remote_sal})
        st.success("Estimated compensation")
        st.markdown(f"```\n{result}\n```")

elif st.session_state.current_page == "Interview Questions":
    st.title("Interview Question Generator")
    st.markdown("Generate technical and behavioral interview questions for different roles and difficulty levels.")
    with st.form("interview_form"):
        role_int = st.text_input("Role", value=sidebar_target_role, key="interview_role")
        difficulty_int = st.selectbox("Difficulty", ["easy", "medium", "hard"], index=1)
        num_technical = st.slider("Number of technical questions", 1, 10, 5)
        num_behavioral = st.slider("Number of behavioral questions", 1, 8, 3)
        focus_areas = st.text_input("Focus areas (optional)", placeholder="system design, analytics, leadership")
        submitted_interview = st.form_submit_button("Generate questions", use_container_width=True)
    if submitted_interview:
        with st.spinner("Generating interview questions..."):
            result = cc_tools.interview_question_generator.invoke({"role": role_int, "difficulty": difficulty_int, "num_behavioral": num_behavioral, "num_technical": num_technical, "focus_areas": focus_areas or None})
        st.success("Interview questions")
        st.markdown(f"```\n{result}\n```")

elif st.session_state.current_page == "Chat Agent":
    st.title("Chat Agent")
    st.markdown("Conversational agent that auto-selects tools and keeps context.")
    st.markdown(f"""<div class="context-card"><div><strong>Target role:</strong> {sidebar_target_role}</div><div><strong>Location:</strong> {sidebar_location}</div><div><strong>Experience:</strong> {sidebar_years_experience} years</div><div><strong>Remote:</strong> {"Yes" if sidebar_is_remote else "No"}</div><div><strong>Model:</strong> {model}</div></div>""", unsafe_allow_html=True)
    st.info("Ask about skills, salary, resumes, or interview prep. The agent will call the right tool automatically.")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    user_prompt = st.chat_input("Chat with the agent")
    st.caption("Press Enter to send • Shift+Enter for a newline")
    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("assistant"):
            if st.session_state.agent is None:
                st.info("Please update the agent to start chatting.")
            else:
                context_suffix = f"\n\nContext: target_role={sidebar_target_role}; location={sidebar_location}; experience={sidebar_years_experience} years; remote={sidebar_is_remote}."
                with st.spinner("Thinking..."):
                    result = st.session_state.agent.invoke({"input": user_prompt + context_suffix})
                output = result.get("output", "I was unable to generate a response.")
                st.markdown(output)
                st.session_state.messages.append({"role": "assistant", "content": output})
