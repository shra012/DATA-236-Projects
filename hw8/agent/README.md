# Kafka Agents System

3-agent system using Kafka for distributed question answering with LangChain.

## Agents

- **Planner**: Reads questions from inbox, creates plans
- **Writer**: Reads plans from tasks, writes answers using LangChain
- **Reviewer**: Reads drafts, reviews and approves answers

## Setup

```bash
# Create venv with uv
uv venv .venv
# Install with uv
uv sync --dev

# And activate venv
source .venv/bin/activate
```

## Run

```bash
python planner.py
python writer.py
python reviewer.py
python send_question.py "Your question here"
python read_final.py
```
