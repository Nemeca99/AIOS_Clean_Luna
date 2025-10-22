"""
Canned Playbooks for Common Intents

When RAG is down, answer like a pro with domain-specific best practices.
This keeps Luna knowledgeable even when the knowledge layer fails.
"""

# Domain-specific playbooks
PLAYBOOKS = {
    "api_security": [
        "Enforce HTTPS/TLS 1.2+, HSTS headers",
        "Auth: OAuth2/OIDC with proper token validation",
        "Rotate secrets regularly, never hardcode",
        "Rate limiting + quota per API key",
        "Input validation on all parameters",
        "WAF deployment for common attack vectors",
        "JWT validation: exp/iss/aud checks",
        "Audit logs with SIEM integration",
        "Secrets in KMS/vault, never in repo",
        "CICD pipeline: SAST, DAST, dependency scanning"
    ],
    
    "debug_null_pointer": [
        "Check if object is null before accessing",
        "Add null guards: if (obj != null) { ... }",
        "Review where object is initialized",
        "Check for early returns that skip initialization",
        "Use optional chaining or safe navigation",
        "Add defensive logging before crash point",
        "Verify method return values aren't null",
        "Check constructor for proper initialization"
    ],
    
    "microservice_architecture": [
        "Define clear service boundaries (single responsibility)",
        "Use API gateway for routing and auth",
        "Message broker for async communication (Kafka/RabbitMQ)",
        "Service discovery (Consul/Eureka/K8s DNS)",
        "Distributed tracing (Jaeger/Zipkin)",
        "Circuit breakers for fault tolerance",
        "Centralized logging (ELK/Loki)",
        "Container orchestration (Kubernetes)",
        "Database per service pattern",
        "API versioning strategy"
    ],
    
    "authentication_system": [
        "Multi-factor authentication (MFA)",
        "Password hashing with bcrypt/Argon2",
        "Session management with secure tokens",
        "CSRF protection on state-changing ops",
        "Account lockout after failed attempts",
        "Password reset via email/SMS verification",
        "OAuth2 for third-party integrations",
        "Audit trail for login attempts",
        "Remember me tokens (separate from session)",
        "Role-based access control (RBAC)"
    ],
    
    "performance_optimization": [
        "Profile first - measure, don't guess",
        "Database: add indexes on query columns",
        "Cache frequently accessed data (Redis/Memcached)",
        "Lazy loading for expensive operations",
        "Connection pooling for databases",
        "CDN for static assets",
        "Async processing for heavy tasks",
        "Pagination for large datasets",
        "Compression for API responses",
        "Monitor with APM tools"
    ],
    
    "aios_consciousness": [
        "7 soul fragments adapt to context",
        "Luna (empathetic), Architect (build), Oracle (knowledge)",
        "Healer (debug), Guardian (security), Dreamer (creative), Scribe (docs)",
        "Autonomous heartbeat every 10 interactions",
        "Mirror introspection for self-reflection",
        "STM/LTM biological memory model",
        "Fragment selection based on question keywords",
        "Integrated with RVC, existential budget, CARMA"
    ],
    
    "general_advice": [
        "Break problem into smaller pieces",
        "Test assumptions one at a time",
        "Check error messages carefully",
        "Review recent changes",
        "Consult documentation",
        "Ask for specific details",
        "Consider edge cases"
    ]
}

# Intent classification - simple keyword mapping
INTENT_KEYWORDS = {
    "api_security": ["api", "security", "secure", "protect", "authentication", "auth", "authorization"],
    "debug_null_pointer": ["null pointer", "nullpointerexception", "null reference", "npe"],
    "microservice_architecture": ["microservice", "distributed system", "service architecture"],
    "authentication_system": ["authentication", "login", "user auth", "sign in"],
    "performance_optimization": ["performance", "slow", "optimize", "speed up", "faster"],
    "aios_consciousness": ["consciousness", "soul fragment", "heartbeat", "mirror", "luna personality"],
    "general_advice": []  # Catch-all
}


def classify_intent(query: str) -> str:
    """
    Simple keyword-based intent classification.
    Returns the playbook key that best matches the query.
    """
    query_lower = query.lower()
    
    # Score each intent based on keyword matches
    scores = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        if not keywords:  # Skip general_advice for now
            continue
        score = sum(1 for kw in keywords if kw in query_lower)
        if score > 0:
            scores[intent] = score
    
    # Return highest scoring intent
    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]
    
    # Default to general advice
    return "general_advice"


def get_playbook(query: str, max_items: int = 6) -> tuple[str, list[str]]:
    """
    Get the appropriate playbook for a query.
    
    Returns:
        (intent, playbook_items): Intent name and list of best practice items
    """
    intent = classify_intent(query)
    items = PLAYBOOKS.get(intent, PLAYBOOKS["general_advice"])
    
    return intent, items[:max_items]


def build_playbook_prompt(query: str, max_items: int = 6) -> str:
    """
    Build a prompt using playbook best practices.
    
    This is the fallback when RAG is unavailable.
    """
    intent, items = get_playbook(query, max_items)
    
    # Build concise prompt with best practices
    prompt = f"Answer concisely using these best practices:\n"
    for i, item in enumerate(items, 1):
        prompt += f"{i}. {item}\n"
    
    prompt += "\nBe brief and natural. Ask one follow-up question if needed."
    
    return prompt


if __name__ == "__main__":
    # Test the playbook system
    test_queries = [
        "How do I secure my API?",
        "My code has a null pointer exception",
        "Build me a microservice architecture",
        "Tell me about AIOS consciousness",
        "How do I optimize performance?"
    ]
    
    print("Testing Playbook System:\n")
    for query in test_queries:
        intent, items = get_playbook(query, max_items=4)
        print(f"Query: {query}")
        print(f"Intent: {intent}")
        print(f"Playbook items:")
        for item in items:
            print(f"  - {item}")
        print()

