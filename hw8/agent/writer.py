#!/usr/bin/env python3
"""
Writer Agent
Reads tasks from 'tasks' topic and writes answer using LangChain, sends to 'drafts' topic
"""

import json
import os
from kafka import KafkaConsumer, KafkaProducer
from datetime import datetime

try:
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.schema import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    print("Warning: LangChain not installed. Using fallback mode.")
    LANGCHAIN_AVAILABLE = False

KAFKA_BROKER = 'localhost:9092'
TASKS_TOPIC = 'tasks'
DRAFTS_TOPIC = 'drafts'
consumer = KafkaConsumer(
    TASKS_TOPIC,
    bootstrap_servers=[KAFKA_BROKER],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='writer-group'
)

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("=" * 70)
print("  WRITER AGENT STARTED")
print("=" * 70)
print(f"Listening to: {TASKS_TOPIC}")
print(f"Publishing to: {DRAFTS_TOPIC}")
if LANGCHAIN_AVAILABLE:
    print("LangChain: ENABLED")
else:
    print("LangChain: DISABLED (using fallback)")
print("Waiting for tasks...\n")


def write_answer_with_langchain(question, plan):
    """
    Uses LangChain to generate an answer
    """
    if not LANGCHAIN_AVAILABLE:
        return write_answer_fallback(question, plan)
    
    try:
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        system_message = SystemMessage(content="""You are a helpful assistant that provides clear, 
        concise, and accurate answers. Follow the provided plan to structure your response.""")
        
        plan_text = "\n".join([f"{i}. {step}" for i, step in enumerate(plan.get('steps', []), 1)])
        
        human_message = HumanMessage(content=f"""Question: {question}

Plan to follow:
{plan_text}

Approach: {plan.get('approach', 'Provide a helpful response')}
Max Length: {plan.get('max_length', '2-3 paragraphs')}

Please provide a well-structured answer following this plan.""")
        
        response = llm.invoke([system_message, human_message])
        return response.content
        
    except Exception as e:
        print(f"LangChain error: {e}")
        print("Falling back to simple answer generation...")
        return write_answer_fallback(question, plan)


def write_answer_fallback(question, plan):
    """
    Fallback answer generation without LangChain
    """
    answer = f"""Based on your question: "{question}"

Here's a structured response following the analysis plan:

This is a generated answer that addresses your question directly. The response is designed to be clear, 
concise, and informative based on the planning steps provided.

The answer considers the key concepts and provides relevant information to help you understand the topic better. 
If you need more specific details or have follow-up questions, please feel free to ask.

Note: This is a demonstration answer. For production use, integrate with an actual LLM API."""
    
    return answer


try:
    for message in consumer:
        print("\n" + "=" * 70)
        print("RECEIVED TASK FROM PLANNER")
        print("=" * 70)
        
        data = message.value
        question_id = data.get('question_id', 'unknown')
        question = data.get('question', '')
        plan = data.get('plan', {})
        
        print(f"Question ID: {question_id}")
        print(f"Question: {question}")
        print(f"Plan Steps: {len(plan.get('steps', []))}")
        
        # Write answer
        print("\nGenerating answer...")
        if LANGCHAIN_AVAILABLE:
            print("Using LangChain with GPT-3.5-turbo...")
        else:
            print("Using fallback answer generation...")
        
        answer = write_answer_with_langchain(question, plan)
        
        # Prepare draft message
        draft_message = {
            "question_id": question_id,
            "question": question,
            "plan": plan,
            "answer": answer,
            "status": "draft",
            "writer_timestamp": datetime.now().isoformat(),
            "planner_timestamp": data.get('planner_timestamp', ''),
            "original_timestamp": data.get('original_timestamp', '')
        }
        
        # Send to drafts topic
        print(f"\nSending draft to {DRAFTS_TOPIC} topic...")
        producer.send(DRAFTS_TOPIC, draft_message)
        producer.flush()
        
        print("\nANSWER GENERATED:")
        print(f"Length: {len(answer)} characters")
        print(f"Preview: {answer[:200]}...")
        
        print("\nDraft sent successfully!")
        print("=" * 70)

except KeyboardInterrupt:
    print("\n\nShutting down Writer agent...")
finally:
    consumer.close()
    producer.close()
    print("Writer agent stopped.")
