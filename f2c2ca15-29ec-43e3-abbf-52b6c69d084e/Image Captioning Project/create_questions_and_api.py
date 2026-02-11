import json
import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import random

# Create comprehensive question bank with 10+ questions per domain
questions_data = {
    "DSA": [
        {"id": "dsa_1", "question": "Implement a function to reverse a linked list. Analyze time and space complexity.", "difficulty": "medium", "topics": ["linked list", "pointers"]},
        {"id": "dsa_2", "question": "Design and implement a LRU (Least Recently Used) cache with O(1) operations.", "difficulty": "hard", "topics": ["hash map", "doubly linked list"]},
        {"id": "dsa_3", "question": "Find the kth largest element in an unsorted array efficiently.", "difficulty": "medium", "topics": ["heap", "quickselect"]},
        {"id": "dsa_4", "question": "Implement a binary search tree with insert, delete, and search operations.", "difficulty": "medium", "topics": ["BST", "tree traversal"]},
        {"id": "dsa_5", "question": "Detect a cycle in a directed graph using appropriate algorithms.", "difficulty": "medium", "topics": ["graph", "DFS"]},
        {"id": "dsa_6", "question": "Find the longest common subsequence between two strings using dynamic programming.", "difficulty": "medium", "topics": ["dynamic programming", "strings"]},
        {"id": "dsa_7", "question": "Implement merge sort and explain its time complexity in best, average, and worst cases.", "difficulty": "medium", "topics": ["sorting", "divide and conquer"]},
        {"id": "dsa_8", "question": "Design a data structure that supports insert, delete, and getRandom in O(1) time.", "difficulty": "hard", "topics": ["hash map", "array"]},
        {"id": "dsa_9", "question": "Find the shortest path in a weighted graph using Dijkstra's algorithm.", "difficulty": "hard", "topics": ["graph", "shortest path"]},
        {"id": "dsa_10", "question": "Implement a trie data structure with insert and search operations for autocomplete.", "difficulty": "medium", "topics": ["trie", "prefix tree"]},
        {"id": "dsa_11", "question": "Solve the N-Queens problem using backtracking.", "difficulty": "hard", "topics": ["backtracking", "recursion"]}
    ],
    "Web": [
        {"id": "web_1", "question": "Explain the difference between var, let, and const in JavaScript. When would you use each?", "difficulty": "easy", "topics": ["JavaScript", "scope"]},
        {"id": "web_2", "question": "What is the event loop in JavaScript? Explain how it handles asynchronous operations.", "difficulty": "medium", "topics": ["JavaScript", "async"]},
        {"id": "web_3", "question": "Implement a debounce function that delays execution until after a specified time.", "difficulty": "medium", "topics": ["JavaScript", "performance"]},
        {"id": "web_4", "question": "Explain CORS and how to handle it in a web application. Provide examples.", "difficulty": "medium", "topics": ["HTTP", "security"]},
        {"id": "web_5", "question": "What are React hooks? Implement a custom hook for form validation.", "difficulty": "medium", "topics": ["React", "hooks"]},
        {"id": "web_6", "question": "Explain the difference between authentication and authorization. Implement JWT-based auth.", "difficulty": "hard", "topics": ["security", "JWT"]},
        {"id": "web_7", "question": "What is CSS specificity? Explain how the cascade works with examples.", "difficulty": "easy", "topics": ["CSS", "styling"]},
        {"id": "web_8", "question": "Implement server-side rendering (SSR) vs client-side rendering (CSR). Compare benefits.", "difficulty": "hard", "topics": ["React", "Next.js"]},
        {"id": "web_9", "question": "Explain how to optimize web application performance. Include lazy loading and code splitting.", "difficulty": "medium", "topics": ["performance", "optimization"]},
        {"id": "web_10", "question": "What is the difference between REST and GraphQL? When would you choose each?", "difficulty": "medium", "topics": ["APIs", "REST"]},
        {"id": "web_11", "question": "Implement WebSocket communication for real-time chat functionality.", "difficulty": "hard", "topics": ["WebSocket", "real-time"]},
        {"id": "web_12", "question": "Explain Progressive Web Apps (PWA) and implement service worker caching.", "difficulty": "hard", "topics": ["PWA", "service workers"]}
    ],
    "Java": [
        {"id": "java_1", "question": "Explain the difference between abstract classes and interfaces in Java. When to use each?", "difficulty": "medium", "topics": ["OOP", "interfaces"]},
        {"id": "java_2", "question": "What is the Java Memory Model? Explain heap vs stack memory allocation.", "difficulty": "medium", "topics": ["JVM", "memory"]},
        {"id": "java_3", "question": "Implement a thread-safe singleton pattern in Java using different approaches.", "difficulty": "medium", "topics": ["design patterns", "concurrency"]},
        {"id": "java_4", "question": "Explain Java Stream API. Implement a complex data transformation pipeline.", "difficulty": "medium", "topics": ["streams", "functional programming"]},
        {"id": "java_5", "question": "What are the differences between ArrayList and LinkedList? When to use each?", "difficulty": "easy", "topics": ["collections", "data structures"]},
        {"id": "java_6", "question": "Implement a custom thread pool executor with task queuing and lifecycle management.", "difficulty": "hard", "topics": ["concurrency", "thread pools"]},
        {"id": "java_7", "question": "Explain Java exception handling. Create a custom exception hierarchy.", "difficulty": "medium", "topics": ["exceptions", "error handling"]},
        {"id": "java_8", "question": "What is reflection in Java? Implement dependency injection using reflection.", "difficulty": "hard", "topics": ["reflection", "annotations"]},
        {"id": "java_9", "question": "Explain Java generics and type erasure. Implement a generic bounded type example.", "difficulty": "medium", "topics": ["generics", "type safety"]},
        {"id": "java_10", "question": "Implement the producer-consumer pattern using BlockingQueue.", "difficulty": "medium", "topics": ["concurrency", "patterns"]},
        {"id": "java_11", "question": "Explain Spring Boot dependency injection and implement a REST API with multiple layers.", "difficulty": "hard", "topics": ["Spring", "DI"]}
    ],
    "Python": [
        {"id": "python_1", "question": "Explain Python's GIL (Global Interpreter Lock). How does it affect multithreading?", "difficulty": "medium", "topics": ["concurrency", "GIL"]},
        {"id": "python_2", "question": "What are Python decorators? Implement a caching decorator with expiration time.", "difficulty": "medium", "topics": ["decorators", "functions"]},
        {"id": "python_3", "question": "Explain the difference between __str__ and __repr__. Implement both for a custom class.", "difficulty": "easy", "topics": ["OOP", "magic methods"]},
        {"id": "python_4", "question": "Implement a context manager using both class-based and decorator approaches.", "difficulty": "medium", "topics": ["context managers", "with statement"]},
        {"id": "python_5", "question": "Explain Python generators and yield. Implement a memory-efficient data pipeline.", "difficulty": "medium", "topics": ["generators", "iterators"]},
        {"id": "python_6", "question": "What is metaclass in Python? Create a singleton metaclass implementation.", "difficulty": "hard", "topics": ["metaclasses", "advanced OOP"]},
        {"id": "python_7", "question": "Implement async/await for concurrent API calls using asyncio.", "difficulty": "medium", "topics": ["asyncio", "concurrency"]},
        {"id": "python_8", "question": "Explain list comprehensions vs generator expressions. When to use each?", "difficulty": "easy", "topics": ["comprehensions", "generators"]},
        {"id": "python_9", "question": "Implement a decorator that measures function execution time with statistics.", "difficulty": "medium", "topics": ["decorators", "profiling"]},
        {"id": "python_10", "question": "What is monkey patching? Implement a safe approach with use cases.", "difficulty": "medium", "topics": ["dynamic typing", "patching"]},
        {"id": "python_11", "question": "Explain Python's descriptor protocol. Implement a validated property descriptor.", "difficulty": "hard", "topics": ["descriptors", "properties"]},
        {"id": "python_12", "question": "Implement a REST API using FastAPI with async database operations and validation.", "difficulty": "hard", "topics": ["FastAPI", "async"]}
    ],
    "System Design": [
        {"id": "sysdesign_1", "question": "Design a URL shortening service like bit.ly. Include database schema and API endpoints.", "difficulty": "medium", "topics": ["scalability", "databases"]},
        {"id": "sysdesign_2", "question": "Design a distributed cache system like Redis. Explain consistency and replication.", "difficulty": "hard", "topics": ["caching", "distributed systems"]},
        {"id": "sysdesign_3", "question": "Design a rate limiting system for an API. Discuss different algorithms and tradeoffs.", "difficulty": "medium", "topics": ["rate limiting", "algorithms"]},
        {"id": "sysdesign_4", "question": "Design a notification system that supports email, SMS, and push notifications.", "difficulty": "hard", "topics": ["messaging", "queue systems"]},
        {"id": "sysdesign_5", "question": "Design a social media feed like Twitter. Handle high read/write throughput.", "difficulty": "hard", "topics": ["feed systems", "scalability"]},
        {"id": "sysdesign_6", "question": "Design a file storage system like Dropbox. Include sync mechanism and conflict resolution.", "difficulty": "hard", "topics": ["storage", "sync"]},
        {"id": "sysdesign_7", "question": "Design a search autocomplete system. Optimize for speed and relevance.", "difficulty": "medium", "topics": ["search", "trie"]},
        {"id": "sysdesign_8", "question": "Design a video streaming platform like YouTube. Handle encoding and CDN delivery.", "difficulty": "hard", "topics": ["streaming", "CDN"]},
        {"id": "sysdesign_9", "question": "Design a distributed message queue like Kafka. Explain partitioning and ordering.", "difficulty": "hard", "topics": ["message queues", "distributed systems"]},
        {"id": "sysdesign_10", "question": "Design a real-time chat system like WhatsApp. Include online status and message delivery.", "difficulty": "hard", "topics": ["real-time", "WebSocket"]},
        {"id": "sysdesign_11", "question": "Design a ride-sharing service like Uber. Include matching algorithm and location tracking.", "difficulty": "hard", "topics": ["geolocation", "matching"]},
        {"id": "sysdesign_12", "question": "Design a monitoring and alerting system for microservices architecture.", "difficulty": "hard", "topics": ["monitoring", "microservices"]}
    ]
}

# Save questions.json
output_path = "questions.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(questions_data, f, indent=2, ensure_ascii=False)

print(f"✅ Created {output_path}")
print(f"\n📊 Questions by domain:")
for domain, questions in questions_data.items():
    print(f"  - {domain}: {len(questions)} questions")
print(f"\n📁 Total questions: {sum(len(q) for q in questions_data.values())}")

# Create Flask API
app = Flask(__name__)
CORS(app)

# AI question generation templates
ai_templates = {
    "DSA": "Generate an algorithm/data structure interview question about {topic}. Include difficulty and complexity analysis.",
    "Web": "Generate a web development interview question about {topic}. Focus on practical scenarios.",
    "Java": "Generate a Java interview question about {topic}. Include OOP concepts or concurrency if relevant.",
    "Python": "Generate a Python interview question about {topic}. Focus on language features or best practices.",
    "System Design": "Generate a system design question about designing {topic}. Include scalability considerations."
}

@app.route('/api/questions', methods=['GET'])
def get_questions():
    """GET /api/questions?domain=<domain>&generate_ai=<bool>"""
    domain = request.args.get('domain', '').strip()
    generate_ai = request.args.get('generate_ai', 'false').lower() == 'true'
    
    if not domain:
        return jsonify({"error": "domain parameter is required"}), 400
    
    if domain not in questions_data:
        return jsonify({
            "error": f"Invalid domain. Must be one of: {', '.join(questions_data.keys())}"
        }), 400
    
    questions = questions_data[domain]
    
    # If AI generation requested, add AI-generated question
    if generate_ai:
        ai_question = generate_ai_question(domain)
        questions = questions + [ai_question]
    
    return jsonify({
        "domain": domain,
        "count": len(questions),
        "questions": questions,
        "ai_generated": generate_ai
    })

def generate_ai_question(domain):
    """Simulate AI-generated question (placeholder - would use LLM in production)"""
    topics = {
        "DSA": ["graph algorithms", "dynamic programming", "tree structures"],
        "Web": ["state management", "API design", "performance optimization"],
        "Java": ["concurrency patterns", "memory management", "design patterns"],
        "Python": ["async programming", "decorators", "context managers"],
        "System Design": ["caching strategy", "load balancing", "data partitioning"]
    }
    
    topic = random.choice(topics.get(domain, ["general"]))
    
    return {
        "id": f"ai_{domain.lower()}_{random.randint(1000, 9999)}",
        "question": f"[AI-Generated] {ai_templates[domain].format(topic=topic)}",
        "difficulty": random.choice(["easy", "medium", "hard"]),
        "topics": [topic, "AI-generated"],
        "ai_generated": True
    }

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": "questions-api"})

# Print API info
print("\n" + "="*60)
print("🚀 QUESTIONS API READY")
print("="*60)
print("\n📡 Endpoints:")
print("  GET /api/questions?domain=<domain>&generate_ai=<bool>")
print("    - Returns questions for specified domain")
print("    - Optional AI generation with generate_ai=true")
print("\n  GET /api/health")
print("    - Health check")
print("\n✅ Available domains:", ", ".join(questions_data.keys()))
print("\n💡 Example usage:")
print("  /api/questions?domain=DSA")
print("  /api/questions?domain=Python&generate_ai=true")
print("\n" + "="*60)

# Return Flask app for further use
questions_api_app = app
print("\n✓ Questions API available as 'questions_api_app'")
print("✓ Run with: questions_api_app.run(port=5000)")
