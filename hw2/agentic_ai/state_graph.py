from __future__ import annotations

import argparse
from typing import Dict, List

from langgraph.graph import END, StateGraph
from langchain_core.messages import SystemMessage, HumanMessage

from agentic_ai.agent_core import AgentState, PlanSchema, ReviewSchema, LLM as llm
from agentic_ai.prompts import (
    PLANNER_SYSTEM_PROMPT,
    REVIEWER_SYSTEM_PROMPT,
    REVIEWER_FOLLOWUP_SYSTEM_PROMPT,
    build_planner_user_prompt,
    build_reviewer_user_prompt,
    build_reviewer_followup_prompt,
)


def planner_node(state: AgentState) -> Dict[str, any]:
    print("--- NODE: Planner ---")

    title = state.get("title", "Untitled")
    task = state.get("task", "Create a brief plan")
    content = state.get("content", "")
    email = state.get("email", "")
    original_issues = state.get("original_issues", [])

    prior_feedback = state.get("reviewer_feedback", {})

    if original_issues:
        print(f"  Addressing {len(original_issues)} tracked issues")
        enhanced_feedback = dict(prior_feedback) if prior_feedback else {}
        enhanced_feedback["original_issues_to_address"] = original_issues
        prior_feedback = enhanced_feedback

    prompt = build_planner_user_prompt(
        title=title, task=task, content=content, email=email, prior_feedback=prior_feedback
    )

    try:
        messages = [SystemMessage(content=PLANNER_SYSTEM_PROMPT), HumanMessage(content=prompt)]
        structured = llm.with_structured_output(PlanSchema)
        result: PlanSchema = structured.invoke(messages)
        try:
            proposal = result.model_dump()
        except Exception:
            proposal = dict(result)
        if "outline" not in proposal or not isinstance(proposal["outline"], list):
            proposal["outline"] = ["Introduction", "Body", "Conclusion"]
    except Exception:
        proposal = {
            "summary": "Fallback plan",
            "outline": ["Introduction", "Body", "Conclusion"],
            "notes": "LLM call or parsing failed; used a fallback plan.",
        }

    return {"planner_proposal": proposal, "reviewer_feedback": {}}


def reviewer_node(state: AgentState) -> Dict[str, any]:
    print("--- NODE: Reviewer ---")
    proposal = state.get("planner_proposal", {}) or {}
    original_issues = state.get("original_issues", [])
    turn_count = state.get("turn_count", 0)

    if not proposal:
        return {
            "reviewer_feedback": {
                "issues": ["No proposal to review"],
                "approved": False,
                "comments": "Planner must produce a proposal first.",
            }
        }

    try:
        if not original_issues:
            print("  First review - identifying initial issues")
            usr_msg = build_reviewer_user_prompt(proposal=proposal)
            messages = [SystemMessage(content=REVIEWER_SYSTEM_PROMPT), HumanMessage(content=usr_msg)]
            structured = llm.with_structured_output(ReviewSchema)
            result: ReviewSchema = structured.invoke(messages)
            try:
                feedback = result.model_dump()
            except Exception:
                feedback = dict(result)
            issues_list = feedback.get("issues", []) or []

            if issues_list:
                print(f"  Found {len(issues_list)} initial issues to track")
                return {
                    "reviewer_feedback": feedback,
                    "original_issues": issues_list
                }
            else:
                feedback["approved"] = True
                feedback["comments"] = "Approved on first review"
                return {"reviewer_feedback": feedback}

        else:
            print(f"  Follow-up review - checking if {len(original_issues)} original issues are resolved")
            usr_msg = build_reviewer_followup_prompt(
                proposal=proposal,
                original_issues=original_issues
            )
            messages = [SystemMessage(content=REVIEWER_FOLLOWUP_SYSTEM_PROMPT), HumanMessage(content=usr_msg)]
            structured = llm.with_structured_output(ReviewSchema)
            result: ReviewSchema = structured.invoke(messages)
            try:
                feedback = result.model_dump()
            except Exception:
                feedback = dict(result)

            issues_list = feedback.get("issues", []) or []
            feedback["approved"] = len(issues_list) == 0
            feedback["comments"] = feedback.get("comments") or (
                "All original issues resolved!" if feedback["approved"] else "Some original issues still need attention.")
            return {"reviewer_feedback": feedback}

    except Exception:
        issues: List[str] = []
        outline = proposal.get("outline", []) if isinstance(proposal, dict) else []
        if not outline:
            issues.append("Proposal missing outline")
        elif len(outline) < 4:
            issues.append("Outline too short (need >= 4 items)")
        if "summary" not in proposal:
            issues.append("Missing summary field")

        feedback = {
            "issues": issues,
            "approved": len(issues) == 0,
            "comments": "Basic validation check",
        }

        if not original_issues and issues:
            return {
                "reviewer_feedback": feedback,
                "original_issues": issues
            }
        else:
            return {"reviewer_feedback": feedback}


def supervisor_node(state: AgentState) -> Dict[str, any]:
    print("--- NODE: Supervisor (state update) ---")
    turn = int(state.get("turn_count", 0)) + 1
    return {"turn_count": turn}


def router_logic(state: AgentState) -> str:
    max_turns = int(state.get("max_turns", 8))
    turn = int(state.get("turn_count", 0))

    print(f"--- ROUTER: Turn {turn}, Max turns: {max_turns} ---")

    if turn >= max_turns:
        print(f"Reached max turns ({max_turns}). Ending.")
        return END

    planner_proposal = state.get("planner_proposal")
    reviewer_feedback = state.get("reviewer_feedback")

    if not planner_proposal:
        print("No proposal yet, routing to planner")
        return "planner"

    if not reviewer_feedback:
        print("No reviewer feedback yet, routing to reviewer")
        return "reviewer"

    if reviewer_feedback.get("issues"):
        print(f"Reviewer found {len(reviewer_feedback.get('issues', []))} issues, routing back to planner")
        return "planner"

    if reviewer_feedback.get("approved") and turn < 4:
        print(f"Approved but only turn {turn}, continuing refinement - routing to planner")
        return "planner"
    print("Final approval received, ending workflow")
    return END


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("planner", planner_node)
    graph.add_node("reviewer", reviewer_node)
    graph.set_entry_point("supervisor")
    graph.add_conditional_edges(
        "supervisor",
        router_logic,
        {"planner": "planner", "reviewer": "reviewer", END: END},
    )
    graph.add_edge("planner", "supervisor")
    graph.add_edge("reviewer", "supervisor")
    return graph.compile()


def parse_arguments():
    parser = argparse.ArgumentParser(description="Agentic AI Planning and Review System")

    parser.add_argument(
        "--title",
        type=str,
        default="Draft a design for using langchain to solve email spam filter",
        help="Title of the planning task"
    )

    parser.add_argument(
        "--content",
        type=str,
        default="The agent should have a list of accepted emails and subjects and should filter out emails that do not match the criteria.",
        help="Content description for the task")

    parser.add_argument(
        "--email",
        type=str,
        default="shravankumar.nagarajan@sjsu.edu",
        help="Email address to include in the context"
    )

    parser.add_argument(
        "--task",
        type=str,
        default="Create a detailed plan with an outline and summary for the given title and content.",
        help="Specific task instructions"
    )

    parser.add_argument(
        "--max-turns",
        type=int,
        default=8,
        help="Maximum number of turns for the workflow"
    )

    return parser.parse_args()


def build_initial_state(args) -> AgentState:
    """Build the initial state from command line arguments"""
    return {
        "title": args.title,
        "content": args.content,
        "email": args.email,
        "task": args.task,
        "turn_count": 0,
        "max_turns": args.max_turns,
    }


def main():
    args = parse_arguments()
    initial_state = build_initial_state(args)

    print(f"\n--- Initial State ---")
    print(f"Title: {initial_state['title']}")
    print(f"Content: {initial_state['content']}")
    print(f"Email: {initial_state['email']}")
    print(f"Task: {initial_state['task']}")
    print(f"Max Turns: {initial_state['max_turns']}")
    print(f"--- Starting Workflow ---")

    app = build_graph()
    print("\n--- Streaming execution ---")
    for event in app.stream(initial_state):
        print(event)
    print("--- END ---")


if __name__ == "__main__":
    main()
