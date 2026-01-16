# Part of Milestone 2: Planning Module Routing Rules
ROUTING_RULES = {
    "legal": [
        "termination", "terminate", "cancel", "cancellation",
        "governing law", "jurisdiction", "venue", "applicable law",
        "liability", "liable", "damages", "limitation of liability",
        "indemnity"
    ],
    "compliance": [
        "gdpr", "data protection", "privacy", "personal data",
        "audit", "auditing", "inspection", "review",
        "regulatory", "regulation", "compliance", "legal requirement",
    ],
    "finance": [
        "payment", "pay", "paid", "payable", "remittance",
        "fee", "fees", "charge", "charges", "cost",
        "penalty", "penalties", "late fee", "late payment",
    ],
    "operations": [
        "deliverable", "deliver", "delivery", "output",
        "timeline", "deadline", "schedule", "due date",
        "sla", "service level", "performance", "kpi", "metric"
    ]
}
from collections import defaultdict

def route_query(query, routing_rules=ROUTING_RULES, threshold=1):
    query_lower = query.lower()
    agent_scores = defaultdict(int)
    agent_matches = defaultdict(list)

    # Scan the query for matching keywords
    for agent, keywords in routing_rules.items():
        for keyword in keywords:
            if keyword.lower() in query_lower:
                agent_scores[agent] += 1
                agent_matches[agent].append(keyword)

    # Identify agents that met the keyword match threshold
    routed_agents = [
        agent for agent, score in agent_scores.items()
        if score >= threshold
    ]

    # Sort by the most matches (highest score)
    routed_agents.sort(key=lambda a: agent_scores[a], reverse=True)

    # Fallback: if no keywords match, the system defaults to checking all agents
    if not routed_agents:
        routed_agents = list(routing_rules.keys())
        reason = "no_matches_fallback_all_agents"
    else:
        reason = "keyword_match"

    return {
        "agents": routed_agents,
        "reason": reason,
        "scores": dict(agent_scores),
        "matches": dict(agent_matches)
    }