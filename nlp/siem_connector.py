from elasticsearch import Elasticsearch
from datetime import datetime
from collections import defaultdict

es = Elasticsearch("http://localhost:9200")
INDEX = "siem-alerts"

# ============================================
# SIEM CONNECTOR
# ============================================

def fetch_alerts(query):
    """Elasticsearch se data fetch karta hai"""
    try:
        response = es.search(index=INDEX, body=query)
        return response
    except Exception as e:
        return {"error": str(e)}

def format_results(response, intent):
    """Raw Elasticsearch response ko readable format mein convert karta hai"""

    if "error" in response:
        return {"type": "error", "message": response["error"]}

    hits = response.get("hits", {}).get("hits", [])
    total = response.get("hits", {}).get("total", {}).get("value", 0)
    aggs = response.get("aggregations", {})

    # Count query result
    if intent == "count_aggregate":
        by_type = aggs.get("by_type", {}).get("buckets", [])
        return {
            "type": "count",
            "total": total,
            "breakdown": [
                {"attack_type": b["key"], "count": b["doc_count"]}
                for b in by_type
            ]
        }

    # Report query result
    if intent == "generate_report":
        over_time = aggs.get("attacks_over_time", {}).get("buckets", [])
        by_type = aggs.get("by_attack_type", {}).get("buckets", [])
        by_ip = aggs.get("by_source_ip", {}).get("buckets", [])
        return {
            "type": "report",
            "total": total,
            "timeline": [
                {
                    "date": b["key_as_string"] if "key_as_string" in b else b["key"],
                    "count": b["doc_count"]
                }
                for b in over_time
            ],
            "by_attack_type": [
                {"type": b["key"], "count": b["doc_count"]}
                for b in by_type
            ],
            "by_source_ip": [
                {"ip": b["key"], "count": b["doc_count"]}
                for b in by_ip
            ],
            "raw_alerts": [h["_source"] for h in hits[:10]]
        }

    # Normal search result
    alerts = []
    for hit in hits:
        source = hit["_source"]
        alerts.append({
            "timestamp": source.get("@timestamp", ""),
            "attack_type": source.get("rule", {}).get("type", "unknown"),
            "source_ip": source.get("source_ip", ""),
            "url": source.get("url", ""),
            "description": source.get("description", ""),
            "status_code": source.get("status_code", "")
        })

    return {
        "type": "alerts",
        "total": total,
        "alerts": alerts
    }

def generate_explanation(result, intent, entities):
    """Enhancement 2 — Plain English explanation generate karta hai"""

    if result["type"] == "error":
        return f"Sorry, I couldn't fetch data: {result['message']}"

    if result["type"] == "count":
        total = result["total"]
        attack_type = entities.get("ATTACK_TYPE", "attacks")
        time_range = entities.get("TIME_RANGE", "the selected period")
        breakdown = result.get("breakdown", [])

        explanation = f"Found {total} {attack_type} attempts during {time_range}."
        if breakdown:
            breakdown_str = ", ".join([f"{b['attack_type']}: {b['count']}" for b in breakdown])
            explanation += f" Breakdown: {breakdown_str}."
        return explanation

    if result["type"] == "report":
        total = result["total"]
        time_range = entities.get("TIME_RANGE", "the selected period")
        by_type = result.get("by_attack_type", [])

        explanation = f"Security report for {time_range}: {total} total alerts detected."
        if by_type:
            top = by_type[0]
            explanation += f" Most common attack type: {top['type']} ({top['count']} incidents)."
        return explanation

    # Normal alerts
    total = result["total"]
    attack_type = entities.get("ATTACK_TYPE", "")
    time_range = entities.get("TIME_RANGE", "selected period")
    alerts = result.get("alerts", [])

    if total == 0:
        return f"No {attack_type} alerts found for {time_range}."

    explanation = f"Found {total} {attack_type} alert(s) during {time_range}."

    if alerts:
        ips = list(set([a["source_ip"] for a in alerts if a["source_ip"]]))
        if ips:
            explanation += f" Source IP(s): {', '.join(ips[:3])}."

        # Why flagged explanation
        if attack_type == "XSS":
            explanation += " These were flagged because requests contained script-injection patterns (e.g. <script>, <iframe>, javascript:) in the URL."
        elif attack_type == "IDOR":
            explanation += " These were flagged because the same IP accessed sequential user IDs in rapid succession — a common IDOR enumeration pattern."

    return explanation

# ============================================
# CONTEXT MANAGER
# ============================================

class ContextManager:
    """Multi-turn conversation ka state maintain karta hai"""

    def __init__(self):
        self.sessions = defaultdict(lambda: {
            "filters": {},
            "last_intent": None,
            "last_result": None,
            "turn_count": 0
        })

    def get_context(self, session_id):
        return self.sessions[session_id]

    def update_context(self, session_id, intent, entities, result):
        session = self.sessions[session_id]

        # Filters merge karo (naye + purane)
        if intent == "filter_followup":
            session["filters"].update(entities)
        else:
            # Naya intent aaya — filters reset karo par time range rakho
            time_range = entities.get("TIME_RANGE")
            session["filters"] = entities.copy()
            if time_range:
                session["filters"]["TIME_RANGE"] = time_range

        session["last_intent"] = intent
        session["last_result"] = result
        session["turn_count"] += 1

    def get_merged_entities(self, session_id, new_entities):
        """Pichle filters + naye entities merge karta hai"""
        context = self.get_context(session_id)
        merged = context["filters"].copy()
        merged.update(new_entities)
        return merged

    def clear_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]

# Global context manager instance
context_manager = ContextManager()

# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    from query_generator import generate_query
    import json

    print("[*] Testing SIEM Connector + Context Manager\n")

    session_id = "test-session-001"

    # Turn 1: XSS attacks today
    print("=" * 50)
    print("Turn 1: 'Show me XSS attempts today'")
    intent = "web_attack_analysis"
    entities = {"ATTACK_TYPE": "XSS", "TIME_RANGE": "today"}

    merged = context_manager.get_merged_entities(session_id, entities)
    query = generate_query(intent, merged)
    response = fetch_alerts(query)
    result = format_results(response, intent)
    explanation = generate_explanation(result, intent, merged)

    context_manager.update_context(session_id, intent, entities, result)

    print(f"Result type: {result['type']}")
    print(f"Total found: {result.get('total', 0)}")
    print(f"Explanation: {explanation}")

    # Turn 2: Filter followup
    print("\n" + "=" * 50)
    print("Turn 2: 'Filter only from IP 172.18.0.1'")
    intent2 = "filter_followup"
    entities2 = {"SOURCE_IP": "172.18.0.1"}

    merged2 = context_manager.get_merged_entities(session_id, entities2)
    print(f"Merged entities (context preserved): {merged2}")

    query2 = generate_query(intent2, merged2)
    response2 = fetch_alerts(query2)
    result2 = format_results(response2, intent2)
    explanation2 = generate_explanation(result2, intent2, merged2)

    context_manager.update_context(session_id, intent2, entities2, result2)

    print(f"Result type: {result2['type']}")
    print(f"Total found: {result2.get('total', 0)}")
    print(f"Explanation: {explanation2}")

    # Turn 3: Count
    print("\n" + "=" * 50)
    print("Turn 3: 'How many total?'")
    intent3 = "count_aggregate"
    entities3 = {}

    merged3 = context_manager.get_merged_entities(session_id, entities3)
    print(f"Merged entities (context preserved): {merged3}")

    query3 = generate_query(intent3, merged3)
    response3 = fetch_alerts(query3)
    result3 = format_results(response3, intent3)
    explanation3 = generate_explanation(result3, intent3, merged3)

    print(f"Result type: {result3['type']}")
    print(f"Total found: {result3.get('total', 0)}")
    print(f"Explanation: {explanation3}")

    print("\n✅ Component 4 test complete!")
