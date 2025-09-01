import json
import random
import requests
import argparse
import time
import re

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
    for i in range(max_retries):
        try:
            response = requests.get(f"{base_url}/api/version", timeout=3)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            time.sleep(1)
    return False

def ask_ollama(prompt, model="smollm:1.7b", base_url="http://127.0.0.1:11434"):
    """Send prompt to Ollama and return response"""
    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=120
        )
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Error: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

def planner_prompt(topic):
    """Create prompt for Planner agent"""
    return f"""Topic: {topic}

Create exactly 3 tags and a summary (max 20 words).

IMPORTANT: Respond with ONLY valid JSON. No other text.

Example format:
{{"tags": ["web", "development", "frontend"], "summary": "Creating user interfaces for websites and applications"}}

Your JSON response for "{topic}":"""

def reviewer_prompt(topic, planner_output):
    """Create prompt for Reviewer agent"""
    return f"""Review the planner's output for the topic "{topic}".

Planner output:
{planner_output}

Your task:
1. Check if the 3 tags are relevant and specific to "{topic}"
2. Verify the summary is accurate and under 20 words
3. If corrections are needed, provide better tags and/or summary
4. If the planner's output is good, keep it as is

Return ONLY valid JSON:
{{"tags": ["corrected_tag1", "corrected_tag2", "corrected_tag3"], "summary": "corrected or original summary"}}"""

def finalizer(reviewer_output):
    """Parse and return final JSON output from reviewer"""
    def extract_json(text):
        """Extract JSON from text response"""
        try:
            # Look for JSON in the response
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end > start:
                json_str = text[start:end]
                # Clean up any malformed JSON
                json_str = json_str.replace('"}', '"')  # Fix trailing quote issue
                parsed = json.loads(json_str)
                
                # Ensure exactly 3 tags
                tags = parsed.get("tags", [])[:3]
                
                # Ensure summary is under 20 words
                summary = parsed.get("summary", "")
                words = summary.split()
                if len(words) > 20:
                    summary = " ".join(words[:20])
                
                return {
                    "tags": tags,
                    "summary": summary
                }
        except Exception as e:
            print(f"JSON parsing error: {e}")
            pass
        
        # Fallback - extract info manually
        lines = text.split('\n')
        tags = []
        summary = ""
        
        for line in lines:
            if 'tags' in line.lower() and '[' in line:
                # Try to extract tags
                match = re.search(r'\[(.*?)\]', line)
                if match:
                    tag_content = match.group(1)
                    tags = [tag.strip().strip('"').strip("'") for tag in tag_content.split(',')]
            elif 'summary' in line.lower() and ':' in line:
                # Try to extract summary
                parts = line.split(':', 1)
                if len(parts) > 1:
                    summary = parts[1].strip().strip('"').strip("'")
                
        return {
            "tags": tags[:3] if tags else ["technology", "innovation", "digital"],
            "summary": summary if summary else "A comprehensive overview of modern technology concepts."
        }
    
    return extract_json(reviewer_output)

def main():
    """Main function to orchestrate the multi-agent workflow"""
    parser = argparse.ArgumentParser(description="Multi-agent system demo")
    parser.add_argument("--topic", type=str, help="Topic to analyze")
    parser.add_argument("--model", type=str, default="smollm:1.7b", help="Ollama model to use")
    parser.add_argument("--base-url", type=str, default="http://127.0.0.1:11434", help="Ollama base URL")
    
    args = parser.parse_args()
    
    # Get topic
    topic = args.topic if args.topic else get_random_topic()
    print(f"Topic: {topic}")
    
    # Check Ollama availability
    if not wait_ollama(args.base_url):
        print("Cannot connect to Ollama. Please ensure it's running.")
        return
    
    # Step 1: Planner generates tags and summary
    print("\n=== PLANNER ===")
    planner_response = ask_ollama(planner_prompt(topic), args.model, args.base_url)
    print(planner_response)
    
    # Step 2: Reviewer validates and corrects if needed
    print("\n=== REVIEWER ===")
    reviewer_response = ask_ollama(reviewer_prompt(topic, planner_response), args.model, args.base_url)
    print(reviewer_response)
    
    # Step 3: Finalizer outputs clean JSON
    print("\n=== FINAL OUTPUT ===")
    final_result = finalizer(reviewer_response)
    print(json.dumps(final_result, indent=2))

if __name__ == "__main__":
    main()