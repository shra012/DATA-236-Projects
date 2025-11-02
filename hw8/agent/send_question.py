#!/usr/bin/env python3
"""
Send Question Script
Sends a question to the 'inbox' topic to start the agent workflow
"""

import json
import sys
from kafka import KafkaProducer
from datetime import datetime
import uuid

# Kafka configuration
KAFKA_BROKER = 'localhost:9092'
INBOX_TOPIC = 'inbox'

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("=" * 70)
print("  SEND QUESTION TO INBOX")
print("=" * 70)


def send_question(question):
    """
    Sends a question to the inbox topic
    """
    question_id = str(uuid.uuid4())[:8]
    
    message = {
        "question_id": question_id,
        "question": question,
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"\nQuestion ID: {question_id}")
    print(f"Question: {question}")
    print(f"Timestamp: {message['timestamp']}")
    print(f"\nSending to {INBOX_TOPIC} topic...")
    
    producer.send(INBOX_TOPIC, message)
    producer.flush()
    
    print("\nQuestion sent successfully!")
    print("\nThe 3-agent workflow will now process your question:")
    print("  1. Planner  -> Creates a plan")
    print("  2. Writer   -> Writes an answer")
    print("  3. Reviewer -> Reviews and approves")
    print("\nCheck the 'final' topic for the approved answer.")
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Question provided as command line argument
        question = " ".join(sys.argv[1:])
    else:
        # Interactive mode
        print("\nEnter your question (or press Ctrl+C to exit):")
        try:
            question = input("> ").strip()
            if not question:
                print("Error: Question cannot be empty")
                sys.exit(1)
        except KeyboardInterrupt:
            print("\n\nCancelled.")
            sys.exit(0)
    
    send_question(question)
    producer.close()
