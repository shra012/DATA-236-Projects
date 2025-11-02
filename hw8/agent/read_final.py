#!/usr/bin/env python3
"""
Read Final Script
Reads approved answers from the 'final' topic
"""

import json
from kafka import KafkaConsumer
import sys

# Kafka configuration
KAFKA_BROKER = 'localhost:9092'
FINAL_TOPIC = 'final'

print("=" * 70)
print("  READING FINAL APPROVED ANSWERS")
print("=" * 70)
print(f"Topic: {FINAL_TOPIC}")
print("Press Ctrl+C to exit\n")

consumer = KafkaConsumer(
    FINAL_TOPIC,
    bootstrap_servers=[KAFKA_BROKER],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='reader-group'
)

try:
    message_count = 0
    
    for message in consumer:
        message_count += 1
        
        print("\n" + "=" * 70)
        print(f"MESSAGE #{message_count}")
        print("=" * 70)
        
        data = message.value
        
        # Display key information
        print(f"\nQuestion ID: {data.get('question_id', 'N/A')}")
        print(f"Status: {data.get('status', 'N/A').upper()}")
        print(f"\nQuestion:")
        print(f"  {data.get('question', 'N/A')}")
        
        print(f"\nAnswer:")
        answer = data.get('answer', 'N/A')
        for line in answer.split('\n'):
            print(f"  {line}")
        
        review = data.get('review', {})
        print(f"\nReview:")
        print(f"  Approved: {review.get('approved', 'N/A')}")
        print(f"  Quality Score: {review.get('quality_score', 'N/A')}/100")
        print(f"  Completeness: {review.get('completeness', 'N/A')}")
        print(f"  Relevance: {review.get('relevance', 'N/A')}")
        
        issues = review.get('issues', [])
        if issues:
            print(f"  Issues: {', '.join(issues)}")
        else:
            print(f"  Issues: None")
        
        print(f"\nTimeline:")
        print(f"  Original: {data.get('original_timestamp', 'N/A')}")
        print(f"  Planner: {data.get('planner_timestamp', 'N/A')}")
        print(f"  Writer: {data.get('writer_timestamp', 'N/A')}")
        print(f"  Reviewer: {data.get('reviewer_timestamp', 'N/A')}")
        
        print(f"\nFull JSON:")
        print(json.dumps(data, indent=2))
        
        print("=" * 70)

except KeyboardInterrupt:
    print("\n\nStopped reading.")
    print(f"Total messages read: {message_count}")
finally:
    consumer.close()
