from datetime import datetime, timedelta

ATTACK_TYPE_MAP = {
    "XSS": "xss",
    "IDOR": "idor",
    "SQLi": "sqli",
    "Brute Force": "brute_force",
    "DDoS": "ddos",
    "RCE": "rce",
    "Path Traversal": "path_traversal",
    "CSRF": "csrf",
    "Phishing": "phishing"
}

def resolve_time_range(time_str):
    now = datetime.utcnow()
    time_str = time_str.lower() if time_str else "today"

    if "today" in time_str:
        start = now.replace(hour=0, minute=0, second=0)
    elif "yesterday" in time_str:
        start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0)
        now = now.replace(hour=0, minute=0, second=0)
    elif "last hour" in time_str or "past 15 minutes" in time_str:
        start = now - timedelta(hours=1)
    elif "last 24 hours" in time_str or "24 hours" in time_str:
        start = now - timedelta(hours=24)
    elif "last night" in time_str:
        start = (now - timedelta(days=1)).replace(hour=20, minute=0, second=0)
        now = now.replace(hour=6, minute=0, second=0)
    elif "this week" in time_str or "last 7 days" in time_str:
        start = now - timedelta(days=7)
    elif "last week" in time_str:
        start = now - timedelta(days=14)
        now = now - timedelta(days=7)
    elif "this month" in time_str or "last 30 days" in time_str:
        start = now - timedelta(days=30)
    elif "last month" in time_str:
        start = now - timedelta(days=60)
        now = now - timedelta(days=30)
    else:
        start = now - timedelta(hours=24)

    return start.isoformat(), now.isoformat()

def generate_query(intent, entities, context=None):
    if context:
        for key, val in context.items():
            if key not in entities:
                entities[key] = val

    time_start, time_end = resolve_time_range(entities.get("TIME_RANGE"))

    must_clauses = [
        {
            "range": {
                "@timestamp": {
                    "gte": time_start,
                    "lte": time_end
                }
            }
        }
    ]

    if intent == "web_attack_analysis":
        attack_type = entities.get("ATTACK_TYPE", "").upper()
        if attack_type in ATTACK_TYPE_MAP:
            must_clauses.append({
                "match": {
                    "rule.group": ATTACK_TYPE_MAP[attack_type]
                }
            })

    elif intent == "search_logs":
        event_type = entities.get("EVENT_TYPE", "")
        if event_type:
            must_clauses.append({
                "match": {
                    "description": event_type
                }
            })

    elif intent == "filter_followup":
        source_ip = entities.get("SOURCE_IP", "")
        severity = entities.get("SEVERITY", "")
        if source_ip and source_ip not in ["that IP", "this IP", "the external IP"]:
            must_clauses.append({
                "match": {"source_ip": source_ip}
            })
        if severity:
            must_clauses.append({
                "match": {"rule.level": severity}
            })

    elif intent == "incident_investigation":
        source_ip = entities.get("SOURCE_IP", "")
        user = entities.get("USER_ACCOUNT", "")
        if source_ip and source_ip not in ["that IP", "this IP", "the external IP"]:
            must_clauses.append({
                "match": {"source_ip": source_ip}
            })
        if user and user not in ["the service account", "unknown users"]:
            must_clauses.append({
                "match": {"user": user}
            })

    if intent == "count_aggregate":
        attack_type = entities.get("ATTACK_TYPE", "").upper()
        if attack_type in ATTACK_TYPE_MAP:
            must_clauses.append({
                "match": {"rule.group": ATTACK_TYPE_MAP[attack_type]}
            })
        return {
            "query": {"bool": {"must": must_clauses}},
            "aggs": {
                "attack_count": {"value_count": {"field": "rule.group"}},
                "by_type": {"terms": {"field": "rule.group"}}
            },
            "size": 0
        }

    if intent == "generate_report":
        return {
            "query": {"bool": {"must": must_clauses}},
            "aggs": {
                "attacks_over_time": {
                    "date_histogram": {
                        "field": "@timestamp",
                        "calendar_interval": "day"
                    }
                },
                "by_attack_type": {"terms": {"field": "rule.group"}},
                "by_source_ip": {"terms": {"field": "source_ip", "size": 10}}
            },
            "size": 100
        }

    return {
        "query": {"bool": {"must": must_clauses}},
        "sort": [{"@timestamp": {"order": "desc"}}],
        "size": 50
    }

if __name__ == "__main__":
    import json

    print("[*] Testing Query Generator\n")

    test_cases = [
        ("web_attack_analysis", {"ATTACK_TYPE": "XSS", "TIME_RANGE": "today"}, None),
        ("web_attack_analysis", {"ATTACK_TYPE": "IDOR", "TIME_RANGE": "yesterday"}, None),
        ("filter_followup", {"SOURCE_IP": "192.168.1.10"}, {"ATTACK_TYPE": "XSS", "TIME_RANGE": "today"}),
        ("count_aggregate", {"ATTACK_TYPE": "XSS", "TIME_RANGE": "this week"}, None),
        ("generate_report", {"TIME_RANGE": "this week"}, None),
        ("incident_investigation", {"SOURCE_IP": "192.168.1.10", "TIME_RANGE": "last 24 hours"}, None),
    ]

    for intent, entities, context in test_cases:
        print(f"Intent: {intent}")
        print(f"Entities: {entities}")
        if context:
            print(f"Context: {context}")
        query = generate_query(intent, entities, context)
        print(f"Query preview: {json.dumps(query)[:150]}...")
        print("-" * 50)
