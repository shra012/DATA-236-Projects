import json
import random
from langchain_ollama import ChatOllama 
import argparse
import time

def get_random_topic():
    """Returns a random tech topic from predefined list"""
    topics = [
        "Machine Learning",
        "Blockchain Technology", 
        "Cloud Computing",
        "Cybersecurity",
        "Internet of Things",
        "Artificial Intelligence",
        "Data Science",
        "DevOps",
        "Microservices",
        "Quantum Computing"
    ]
    return random.choice(topics)

def wait_ollama(base_url="http://127.0.0.1:11434", max_retries=5):
    """Check if Ollama service is running"""
    import requests
    for i in range(max_retries):
        try:
            response = requests.get(f"{base_url}/api/version", timeout=3)
            if response.status_code == 200:
                return True
        except Exception:
            time.sleep(1)
    return False

def ask_ollama(prompt, model="smollm:1.7b", base_url="http://127.0.0.1:11434"):
    """Send prompt to Ollama using LangChain and return response"""
    llm = ChatOllama(
        model=model,
        temperature=0.2,
        base_url=base_url,
        num_ctx=2048,
        format="json",
    )
    response = llm.invoke(prompt)
    return response.content

def planner_prompt(topic, content=None):
        """Prompt for Planner agent to generate tags and summary with thought and message."""
        content_section = f"\nContent to analyze: {content}\n" if content else ""
        return f'''You are Planner.
Think step by step. First, write a brief thought about the topic{" and provided content" if content else ""}.
Then, write a one-sentence message summarizing the topic{" based on the content" if content else ""}.
Then, generate a JSON object with:
    - tags: 3 concise, domain-appropriate tags
    - summary: a <=25-word one-sentence summary
    - issues: [] (empty list)
Respond ONLY with a JSON object in this format:
{{
    "thought": "...",
    "message": "...",
    "data": {{
        "tags": ["tag1", "tag2", "tag3"],
        "summary": "..."
    }},
    "issues": []
}}
Topic: {topic}{content_section}
'''

def reviewer_prompt(topic, planner_output, content=None):
        """Prompt for Reviewer agent to validate and possibly revise tags/summary, with thought and message."""
        content_section = f"\nContent to analyze: {content}\n" if content else ""
        return f'''You are Reviewer.
Given the topic{" and provided content" if content else ""} and the Planner's JSON, check if the tags and summary are clear, correct, and relevant.
If not, revise them. Write a brief thought and a one-sentence message.
Respond ONLY with a JSON object in this format:
{{
    "thought": "...",
    "message": "...",
    "data": {{
        "tags": ["tag1", "tag2", "tag3"],
        "summary": "..."
    }},
    "issues": []
}}
Topic: {topic}{content_section}
Planner JSON: {json.dumps(planner_output, ensure_ascii=False)}
'''

def finalizer(planner_json, reviewer_json, topic):
    """Combine and print the finalized output and publish package."""
    # Compose finalized output
    finalized = {
        "thought": reviewer_json.get("thought", ""),
        "message": reviewer_json.get("message", ""),
        "data": reviewer_json.get("data", {}),
        "issues": reviewer_json.get("issues", []),
    }
    print("\n=== Finalized output ===\n")
    print(json.dumps(finalized, indent=2, ensure_ascii=False))

    # Compose publish package
    publish = {
        "title": topic,
        "thought": planner_json.get("thought", ""),
        "message": planner_json.get("message", ""),
        "agents": [
            {"role": "Planner", "summary": planner_json.get("data", {}).get("summary", "")},
            {"role": "Reviewer", "summary": reviewer_json.get("data", {}).get("summary", "")},
        ],
        "final": reviewer_json.get("data", {})
    }
    print("\n=== Publish Package ===\n")
    print(json.dumps(publish, indent=2, ensure_ascii=False))
    return finalized

def main():
    """Main function to orchestrate the multi-agent workflow"""
    parser = argparse.ArgumentParser(description="Two-agent (Planner, Reviewer) demo with strict JSON finalizer.")
    parser.add_argument("--model", default="smollm:1.7b")
    parser.add_argument("--title", type=str, help="Topic to analyze")
    parser.add_argument("--content", type=str, help="Content to analyze for the given topic")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    args = parser.parse_args()

    topic = args.title if args.title else get_random_topic()
    content = args.content
    print(f"Topic: {topic}")
    if content:
        print(f"Content: {content[:100]}{'...' if len(content) > 100 else ''}")

    if not wait_ollama(args.base_url):
        print("Cannot connect to Ollama. Please ensure it's running.")
        return

    print("\n--- Planner ---\n")
    planner_raw = ask_ollama(planner_prompt(topic, content), args.model, args.base_url)
    print(planner_raw)
    try:
        planner_json = json.loads(planner_raw[planner_raw.find('{'):planner_raw.rfind('}')+1])
    except Exception:
        print("Planner did not return valid JSON.")
        return

    print("\n--- Reviewer ---\n")
    reviewer_raw = ask_ollama(reviewer_prompt(topic, planner_json, content), args.model, args.base_url)
    print(reviewer_raw)
    try:
        reviewer_json = json.loads(reviewer_raw[reviewer_raw.find('{'):reviewer_raw.rfind('}')+1])
    except Exception:
        print("Reviewer did not return valid JSON.")
        return

    finalizer(planner_json, reviewer_json, topic)

if __name__ == "__main__":
    main()