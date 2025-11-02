#!/usr/bin/env python3
"""
Planner Agent
Reads questions from 'inbox' topic and creates a plan, sends to 'tasks' topic
"""

import json
import time
from kafka import KafkaConsumer, KafkaProducer
from datetime import datetime

KAFKA_BROKER = 'localhost:9092'
INBOX_TOPIC = 'inbox'
TASKS_TOPIC = 'tasks'
consumer = KafkaConsumer(
    INBOX_TOPIC,
    bootstrap_servers=[KAFKA_BROKER],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='planner-group'
)

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("=" * 70)
print("  PLANNER AGENT STARTED")
print("=" * 70)
print(f"Listening to: {INBOX_TOPIC}")
print(f"Publishing to: {TASKS_TOPIC}")
print("Waiting for questions...\n")


def create_plan(question):
    """
    Creates a structured plan for answering the question
    """
    print(f"\nCreating plan for: {question}")
    
    plan = {
        "steps": [
            "Understand the core question",
            "Identify key concepts to address",
            "Structure a clear and concise answer",
            "Ensure accuracy and completeness"
        ],
        "approach": "Provide a factual, helpful response",
        "max_length": "2-3 paragraphs"
    }
    
    return plan


try:
    for message in consumer:
        print("\n" + "=" * 70)
        print("RECEIVED MESSAGE FROM INBOX")
        print("=" * 70)
        
        data = message.value
        question_id = data.get('question_id', 'unknown')
        question = data.get('question', '')
        timestamp = data.get('timestamp', '')
        
        print(f"Question ID: {question_id}")
        print(f"Question: {question}")
        print(f"Received at: {timestamp}")
        
        plan = create_plan(question)
        
        task_message = {
            "question_id": question_id,
            "question": question,
            "plan": plan,
            "status": "planned",
            "planner_timestamp": datetime.now().isoformat(),
            "original_timestamp": timestamp
        }
        
        print(f"\nSending plan to {TASKS_TOPIC} topic...")
        producer.send(TASKS_TOPIC, task_message)
        producer.flush()
        
        print("\nPLAN CREATED:")
        print(f"  Steps: {len(plan['steps'])}")
        for i, step in enumerate(plan['steps'], 1):
            print(f"    {i}. {step}")
        print(f"  Approach: {plan['approach']}")
        print(f"  Max Length: {plan['max_length']}")
        
        print("\nTask sent successfully!")
        print("=" * 70)

except KeyboardInterrupt:
    print("\n\nShutting down Planner agent...")
finally:
    consumer.close()
    producer.close()
    print("Planner agent stopped.")
