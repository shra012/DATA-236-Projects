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
python evaluate_geval.py --question-id <id-shown-when-sent>
```

## Automated Evaluation (GEval + OpenAI)

After the reviewer publishes to the `final` topic, run `evaluate_geval.py` to automatically
score that workflow. The script pulls the correlated plan (from `tasks`), draft (from
`drafts`), and reviewer-approved answer (from `final`) using the shared `question_id`, then
invokes DeepEval's `GEval` metric backed by an OpenAI judge model. Three scores are reported:

- **Plan Quality** – checks whether the planner's structure is actionable and aligned
- **Helpfulness** – run independently for the writer and reviewer answers
- **Final vs. Draft Improvement** – measures if the reviewer meaningfully refined the draft

Set `OPENAI_API_KEY` and (optionally) `OPENAI_MODEL` (defaults to `gpt-4o-mini`). You can also
set `DEEPEVAL_API_KEY` if your DeepEval installation requires it. The evaluator exits early
with guidance if the key is missing.
