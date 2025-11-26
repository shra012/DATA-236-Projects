# Career Counseling Agent

Streamlit app that wraps an OpenAI model (defaults to `gpt-5-nano`) + LangChain agent to help with career planning. It automatically selects between four tools—Skills Gap Analyzer, Resume Scorer, Salary Estimator, and Interview Question Generator—while keeping conversation memory across turns. The UI has dedicated tabs for each workflow (skills gap upload + job scrape, resume scoring, salary + interview questions) and a chat agent tab.

## Setup

1) Create the virtual environment and install deps (already in `pyproject.toml`):
```bash
cd /Users/hiruzen/Programming/Projects/DATA-236-Projects/hw11
source .venv/bin/activate
uv sync
```

2) Add your OpenAI key to a local `.env` (auto-loaded via `python-dotenv`):
```bash
cp .env.example .env
# then edit .env and set OPENAI_API_KEY=sk-...
# or export OPENAI_API_KEY=sk-... if you prefer shell env vars
```

3) Run the app:
```bash
streamlit run app.py
```

## How it works

- LangChain agent (`create_openai_tools_agent`) with conversation buffer memory.
- Uses OpenAI `gpt-5-nano` by default; temperature and model variant (gpt-5-nano, gpt-5-mini, gpt-4o) configurable from the sidebar.
- Tabs:
  - **Skills Gap Analyzer**: upload resume (PDF/text), paste or scrape job description from a URL, see detected skills + learning path.
  - **Resume Scorer**: upload or paste resume text, get a 0–10 score with fixes, see strengths/gaps in color, and generate a downloadable improved resume PDF.
  - **Comp & Interview**: estimate salary by title/location/experience/remote and generate interview questions by role/difficulty.
  - **Chat Agent**: conversational experience that auto-selects tools and keeps context.
- Tools used under the hood:
  - `skills_gap_analyzer`: compares your skills to a target role/JD and proposes a learning path.
  - `resume_scorer`: heuristic 0–10 score plus actionable edits.
  - `salary_estimator`: region- and experience-adjusted bands.
  - `interview_question_generator`: technical + behavioral questions by difficulty.
- Sidebar controls: model/temperature, default target role/location/experience/remote flag, and reset chat.

## Example prompts tried

- “My skills: Python, SQL, Tableau, Airflow. Target: Data Scientist at a fintech. What gaps?”
- “Estimate salary for a remote ML Engineer in Seattle with 5 years of experience.”
- “Here’s my resume summary (paste). Score it for backend roles and give fixes.”
- “Give me hard PM interview questions focused on product sense and metrics.”

## Notes

- Screenshots: run the app and capture the Skills Gap tab (with scraped job), Resume Scorer tab, and Comp & Interview tab showing responses.
- Tools prefer grounded, skimmable outputs; the agent keeps context from earlier turns.
