from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

PLANNER_SYSTEM_PROMPT = (
    "You are a helpful planner who creates comprehensive, detailed proposals. "
    "When given feedback, carefully address all suggestions and improve the proposal. "
    "Make each iteration more detailed and thorough than the previous version. "
    "Produce output that matches the given schema with rich, actionable content."
)

REVIEWER_SYSTEM_PROMPT = (
    "You are a rigorous proposal reviewer. Check that: "
    "1) 'summary' is a non-empty string; "
    "2) 'outline' is a non-empty list of section titles; "
    "3) The outline has at least 4 items. "
    "Additionally, provide constructive feedback for improvement even if basic requirements are met. "
    "Consider: clarity, completeness, logical flow, technical depth, and practical implementation details. "
    "In early reviews, suggest enhancements to make the proposal more comprehensive."
)

REVIEWER_FOLLOWUP_SYSTEM_PROMPT = (
    "You are a meticulous follow-up reviewer checking if specific issues have been resolved. "
    "Your task is to be CRITICAL and THOROUGH when evaluating whether each original issue "
    "has been truly and completely addressed. "
    "Be skeptical - do not easily approve unless the issue is genuinely resolved with concrete details. "
    "For each original issue: "
    "1) Look for specific, detailed responses that directly address the concern "
    "2) Verify that solutions are concrete, not just vague promises "
    "3) Check that technical details, numbers, examples, or implementation specifics are provided where needed "
    "4) If an issue is only partially addressed or lacks sufficient detail, mark it as unresolved "
    "5) Only mark an issue as resolved if you can point to specific text that comprehensively answers the concern "
    "Be strict - it's better to require another iteration than to approve incomplete solutions."
)


def build_planner_user_prompt(
    *,
    title: str,
    task: str,
    content: str,
    email: str,
    prior_feedback: Optional[Dict[str, Any]] = None,
) -> str:
    if prior_feedback:
        # Check if we have original issues to focus on
        original_issues = prior_feedback.get("original_issues_to_address", [])
        if original_issues:
            issues_text = "\n".join(f"- {issue}" for issue in original_issues)
            feedback_notes = (
                f"\n\nORIGINAL ISSUES TO ADDRESS:\n{issues_text}\n\n"
                f"LATEST REVIEWER FEEDBACK:\n"
                f"{json.dumps(prior_feedback, ensure_ascii=False, indent=2)}\n\n"
                f"Focus on resolving the original issues listed above. "
                f"Make sure each issue is directly addressed in your updated proposal."
            )
        else:
            feedback_notes = (
                f"\n\nPREVIOUS REVIEWER FEEDBACK TO ADDRESS:\n"
                f"{json.dumps(prior_feedback, ensure_ascii=False, indent=2)}\n"
                f"Please carefully address all issues mentioned above and improve the proposal accordingly."
            )
    else:
        feedback_notes = "\n\nThis is your first draft - make it comprehensive and detailed."

    return (
        f"Task: {task}\n"
        f"Title: {title}\n"
        f"Content: {content}\n"
        f"Email: {email}\n"
        f"Produce a JSON plan with keys: summary, outline (list of steps), notes."
        f"{feedback_notes}"
    )


def build_reviewer_user_prompt(*, proposal: Dict[str, Any]) -> str:
    return (
        f"Proposal JSON:\n{json.dumps(proposal, ensure_ascii=False)}\n"
        "Review this proposal thoroughly. Consider:\n"
        "- Are the requirements met? (summary, outline with 4+ items)\n"
        "- Could the outline be more detailed or comprehensive?\n"
        "- Does the summary capture all key aspects?\n"
        "- Are there missing technical considerations?\n"
        "- Would additional sections improve the proposal?\n"
        "List specific issues for improvement, or return no issues if truly comprehensive."
    )


def build_reviewer_followup_prompt(*, proposal: Dict[str, Any], original_issues: List[str]) -> str:
    issues_text = "\n".join(f"{i + 1}. {issue}" for i, issue in enumerate(original_issues))
    return (
        f"ORIGINAL ISSUES TO VERIFY (BE CRITICAL):\n{issues_text}\n\n"
        f"UPDATED PROPOSAL:\n{json.dumps(proposal, ensure_ascii=False, indent=2)}\n\n"
        "CRITICAL REVIEW INSTRUCTIONS:\n"
        "Go through each numbered issue above and check if it has been COMPLETELY resolved with specific details.\n\n"
        "For each issue, ask yourself:\n"
        "- Is there concrete, detailed text that directly addresses this specific concern?\n"
        "- Are there specific examples, numbers, implementation details, or technical specifics provided?\n"
        "- Would this solution actually work in practice, or is it just vague promises?\n"
        "- Has the issue been addressed comprehensively, or only superficially?\n\n"
        "STRICT CRITERIA:\n"
        "- If an issue asks for 'specific details' but you only see generic statements → UNRESOLVED\n"
        "- If an issue asks for 'examples' but no concrete examples are provided → UNRESOLVED\n"
        "- If an issue asks for 'numbers/metrics' but no specific values are given → UNRESOLVED\n"
        "- If the response is vague or hand-wavy instead of concrete → UNRESOLVED\n\n"
        "OUTPUT ONLY the issues that remain unresolved. Be strict - don't approve unless genuinely satisfied.\n"
        "If ALL issues are truly and completely resolved with concrete details, return an empty issues list."
    )
