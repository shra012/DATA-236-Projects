#!/usr/bin/env python3
"""
Reviewer Agent
Reads drafts from 'drafts' topic, reviews and approves, sends to 'final' topic
"""

import json
from kafka import KafkaConsumer, KafkaProducer
from datetime import datetime

KAFKA_BROKER = 'localhost:9092'
DRAFTS_TOPIC = 'drafts'
FINAL_TOPIC = 'final'
consumer = KafkaConsumer(
    DRAFTS_TOPIC,
    bootstrap_servers=[KAFKA_BROKER],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='reviewer-group'
)

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("=" * 70)
print("  REVIEWER AGENT STARTED")
print("=" * 70)
print(f"Listening to: {DRAFTS_TOPIC}")
print(f"Publishing to: {FINAL_TOPIC}")
print("Waiting for drafts to review...\n")


def review_answer(question, answer, plan):
    """
    Reviews the answer and provides feedback
    """
    print(f"\nReviewing answer for: {question}")
    
    issues = []
    
    if not answer or len(answer.strip()) < 50:
        issues.append("Answer is too short")
    
    if len(answer) > 2000:
        issues.append("Answer might be too verbose")
    
    question_lower = question.lower()
    answer_lower = answer.lower()
    
    question_words = set(question_lower.split())
    answer_words = set(answer_lower.split())
    common_words = question_words.intersection(answer_words)
    
    if len(common_words) < 2:
        issues.append("Answer may not address the question directly")
    
    approved = len(issues) == 0
    
    review = {
        "approved": approved,
        "issues": issues,
        "quality_score": 100 - (len(issues) * 20),
        "completeness": "good" if len(answer) > 100 else "needs_improvement",
        "relevance": "high" if len(common_words) >= 3 else "medium"
    }
    
    return review


try:
    for message in consumer:
        print("\n" + "=" * 70)
        print("RECEIVED DRAFT FROM WRITER")
        print("=" * 70)
        
        data = message.value
        question_id = data.get('question_id', 'unknown')
        question = data.get('question', '')
        answer = data.get('answer', '')
        plan = data.get('plan', {})
        
        print(f"Question ID: {question_id}")
        print(f"Question: {question}")
        print(f"Answer Length: {len(answer)} characters")
        
        print("\nReviewing answer...")
        review = review_answer(question, answer, plan)
        
        final_message = {
            "question_id": question_id,
            "question": question,
            "answer": answer,
            "plan": plan,
            "review": review,
            "status": "approved" if review['approved'] else "rejected",
            "reviewer_timestamp": datetime.now().isoformat(),
            "writer_timestamp": data.get('writer_timestamp', ''),
            "planner_timestamp": data.get('planner_timestamp', ''),
            "original_timestamp": data.get('original_timestamp', '')
        }
        
        print(f"\nSending to {FINAL_TOPIC} topic...")
        producer.send(FINAL_TOPIC, final_message)
        producer.flush()
        
        print("\nREVIEW RESULTS:")
        print(f"  Status: {final_message['status'].upper()}")
        print(f"  Approved: {'YES' if review['approved'] else 'NO'}")
        print(f"  Quality Score: {review['quality_score']}/100")
        print(f"  Completeness: {review['completeness']}")
        print(f"  Relevance: {review['relevance']}")
        
        if review['issues']:
            print(f"  Issues Found: {len(review['issues'])}")
            for issue in review['issues']:
                print(f"    - {issue}")
        else:
            print("  Issues Found: None")
        
        print("\nFinal message sent successfully!")
        print("=" * 70)

except KeyboardInterrupt:
    print("\n\nShutting down Reviewer agent...")
finally:
    consumer.close()
    producer.close()
    print("Reviewer agent stopped.")
