#!/usr/bin/env python3
"""Automated evaluation for the Kafka agent workflow using GEval."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

from kafka import KafkaConsumer

from deepeval.metrics import GEval
from deepeval.models import GPTModel
from deepeval.test_case import LLMTestCase, LLMTestCaseParams


KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TOPICS = {
    "plan": os.getenv("PLAN_TOPIC", "tasks"),
    "draft": os.getenv("DRAFT_TOPIC", "drafts"),
    "final": os.getenv("FINAL_TOPIC", "final"),
}


@dataclass
class WorkflowSample:
    question_id: str
    question: str
    plan: Dict[str, Any]
    draft: Dict[str, Any]
    final: Dict[str, Any]


def build_model() -> GPTModel:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Please export it before running the evaluator."
        )

    return GPTModel(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        _openai_api_key=api_key,
        temperature=float(os.getenv("EVAL_TEMPERATURE", "0")),
    )


def fetch_message(topic: str, question_id: str, timeout: float = 8.0) -> Dict[str, Any]:
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=[KAFKA_BROKER],
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        consumer_timeout_ms=int(timeout * 1000),
    )

    match: Optional[Dict[str, Any]] = None
    try:
        for message in consumer:
            payload = message.value
            if payload.get("question_id") == question_id:
                match = payload
    finally:
        consumer.close()

    if not match:
        raise RuntimeError(
            f"No message with question_id={question_id} found on topic '{topic}'."
        )

    return match


def render_plan(plan: Dict[str, Any]) -> str:
    steps: Iterable[str] = plan.get("steps", [])
    approach = plan.get("approach", "")
    length = plan.get("max_length", "")
    rendered_steps = "\n".join(
        f"Step {idx + 1}: {step}" for idx, step in enumerate(steps)
    ) or "(No steps provided)"
    return f"Approach: {approach}\nMax Length: {length}\n{rendered_steps}"


def plan_quality_metric(model: GPTModel) -> GEval:
    return GEval(
        name="Plan Quality",
        criteria=(
            "Score how well the plan decomposes the user's question into actionable,"
            " logically ordered steps that would help another agent craft an answer."
        ),
        evaluation_steps=[
            "Does the plan restate key goals from the question?",
            "Are the steps specific and sequenced?",
            "Would the plan enable a competent writer to respond fully?",
        ],
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        model=model,
        threshold=float(os.getenv("PLAN_QUALITY_THRESHOLD", "0.6")),
    )


def helpfulness_metric(stage_name: str, model: GPTModel) -> GEval:
    return GEval(
        name=f"{stage_name} Helpfulness",
        criteria=(
            f"Rate whether the {stage_name.lower()} answer fully addresses the question,"
            " maintains accuracy, and remains clear and helpful."
        ),
        evaluation_steps=[
            "Check coverage of the user's ask",
            "Check factuality and usefulness",
            "Check structure and clarity",
        ],
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.CONTEXT,
        ],
        model=model,
        threshold=float(os.getenv("HELPFULNESS_THRESHOLD", "0.65")),
    )


def improvement_metric(model: GPTModel) -> GEval:
    return GEval(
        name="Final vs Draft Improvement",
        criteria=(
            "Compare the reviewer-approved answer to the writer's draft. Score higher if the"
            " reviewer improved accuracy, clarity, completeness, or structure."
        ),
        evaluation_steps=[
            "Identify concrete differences between draft and final",
            "Determine if changes fix issues or add value",
            "Penalize regressions or minimal edits",
        ],
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.CONTEXT,
        ],
        model=model,
        threshold=float(os.getenv("IMPROVEMENT_THRESHOLD", "0.5")),
    )


def evaluate(sample: WorkflowSample, model: GPTModel) -> Dict[str, Dict[str, Any]]:
    question = sample.question

    plan_case = LLMTestCase(
        input=question,
        actual_output=render_plan(sample.plan),
    )

    writer_case = LLMTestCase(
        input=question,
        actual_output=sample.draft.get("answer", ""),
        context=[render_plan(sample.plan)],
    )

    reviewer_case = LLMTestCase(
        input=question,
        actual_output=sample.final.get("answer", ""),
        context=[render_plan(sample.plan)],
    )

    improvement_case = LLMTestCase(
        input=question,
        actual_output=sample.final.get("answer", ""),
        context=[
            "Writer Draft:\n" + sample.draft.get("answer", "(missing)")
        ],
    )

    plan_metric = plan_quality_metric(model)
    writer_metric = helpfulness_metric("Writer", model)
    reviewer_metric = helpfulness_metric("Reviewer", model)
    delta_metric = improvement_metric(model)

    plan_metric.measure(plan_case)
    writer_metric.measure(writer_case)
    reviewer_metric.measure(reviewer_case)
    delta_metric.measure(improvement_case)

    return {
        "plan_quality": {
            "score": plan_metric.score,
            "reason": plan_metric.reason,
            "threshold": plan_metric.threshold,
        },
        "writer_helpfulness": {
            "score": writer_metric.score,
            "reason": writer_metric.reason,
            "threshold": writer_metric.threshold,
        },
        "reviewer_helpfulness": {
            "score": reviewer_metric.score,
            "reason": reviewer_metric.reason,
            "threshold": reviewer_metric.threshold,
        },
        "final_vs_draft": {
            "score": delta_metric.score,
            "reason": delta_metric.reason,
            "threshold": delta_metric.threshold,
        },
    }


def load_workflow(question_id: str) -> WorkflowSample:
    plan = fetch_message(TOPICS["plan"], question_id)
    draft = fetch_message(TOPICS["draft"], question_id)
    final = fetch_message(TOPICS["final"], question_id)

    question = final.get("question") or draft.get("question") or plan.get("question")
    if not question:
        raise RuntimeError("Question text missing from workflow messages.")

    return WorkflowSample(
        question_id=question_id,
        question=question,
        plan=plan.get("plan", plan),
        draft=draft,
        final=final,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate the Kafka agent pipeline outputs with GEval.",
    )
    parser.add_argument(
        "--question-id",
        required=True,
        help="Correlation/question ID emitted by send_question.py",
    )
    parser.add_argument(
        "--show-json",
        action="store_true",
        help="Print the raw plan/draft/final payloads before scoring.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        sample = load_workflow(args.question_id)
    except RuntimeError as exc:
        print(f"[error] {exc}")
        sys.exit(1)

    if args.show_json:
        print("\n=== Captured Messages ===")
        print("Plan:", json.dumps(sample.plan, indent=2))
        print("Draft:", json.dumps(sample.draft, indent=2))
        print("Final:", json.dumps(sample.final, indent=2))

    try:
        model = build_model()
    except RuntimeError as exc:
        print(f"[error] {exc}")
        sys.exit(1)

    print(f"\nEvaluating workflow for question_id={sample.question_id}...")
    scores = evaluate(sample, model)

    print("\n=== GEval Scores ===")
    for label, payload in scores.items():
        pct = round(payload["score"] * 100, 1)
        threshold_pct = round(payload["threshold"] * 100, 1)
        print(
            f"{label.replace('_', ' ').title()}: {pct}% (threshold {threshold_pct}%)\n"
            f"  Reason: {payload['reason']}\n"
        )


if __name__ == "__main__":
    main()
