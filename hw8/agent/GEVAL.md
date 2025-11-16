# GEval Evaluation Report

| Metric | Score | Pass Threshold | Notes |
| --- | --- | --- | --- |
| Plan Quality | _fill after running_ | 60% | Judge checks if the planner delivered actionable, sequenced steps. |
| Writer Helpfulness | _fill after running_ | 65% | Evaluates how well the draft answers the original prompt. |
| Reviewer Helpfulness | _fill after running_ | 65% | Ensures the reviewer’s final answer remains accurate and helpful. |
| Final vs. Draft Improvement | _fill after running_ | 50% | Captures whether the reviewer meaningfully improved the draft. |

## How to Produce These Scores

1. Start Zookeeper/Kafka and launch the planner, writer, and reviewer agents.
2. Send a test question via `python send_question.py "<your question>"` and note the printed `question_id`.
3. After the reviewer forwards the approved answer to the `final` topic, run:

   ```bash
   OPENAI_API_KEY=sk-... python evaluate_geval.py --question-id <id> --show-json
   ```

4. Copy the four reported scores into the table above. If a score is below its threshold, inspect the `Reason` strings printed by the evaluator to understand what the judge model disliked.

## Reflection (≈150 words)

Automated evaluation closes the loop between our Kafka agents and their actual output quality. GEval turns subjective review work into structured metrics: plan quality highlights whether the Planner is feeding downstream agents actionable steps; writer and reviewer helpfulness isolate which stage causes regressions; the improvement metric proves that the Reviewer adds tangible value. Because everything is keyed by `question_id`, we can correlate lag spikes in a topic with dips in evaluation, revealing coordination bugs faster than manual tracing. It also accelerates iteration: we can tweak the Writer prompt, replay a question, and instantly see if the helpfulness score climbs. Finally, GEval produces consistent, explainable rationales that we can share with teammates or include in postmortems. Instead of guessing why a final answer went off the rails, we ask the judge model, store the justification next to the Kafka offsets, and plan targeted fixes for whichever agent regressed.
