import json
import random

attack_types = ["XSS", "IDOR", "SQLi", "Brute Force", "DDoS", "RCE", "Path Traversal", "CSRF", "Phishing"]
time_ranges = ["today", "yesterday", "this week", "last 24 hours", "last night", "this month", "in the last hour", "past 15 minutes"]
event_types = ["failed logins", "authentication attempts", "malware detections", "suspicious logins", "privilege escalations", "lateral movement"]
severities = ["critical", "high", "medium", "low"]
ips = ["192.168.1.10", "10.0.0.5", "172.16.0.50", "that IP", "this IP", "the external IP"]
user_accounts = ["admin", "root", "system", "the service account", "unknown users"]

templates = {
    "web_attack_analysis": [
        "Show me {ATTACK_TYPE} attempts {TIME_RANGE}",
        "Any {ATTACK_TYPE} attacks {TIME_RANGE}",
        "Find {ATTACK_TYPE} activity {TIME_RANGE}",
        "Did we get any {ATTACK_TYPE} alerts {TIME_RANGE}?",
        "Pull logs for {ATTACK_TYPE} exploits {TIME_RANGE}",
        "Check for {ATTACK_TYPE} signatures {TIME_RANGE}"
    ],
    "search_logs": [
        "What {EVENT_TYPE} occurred {TIME_RANGE}",
        "Show {EVENT_TYPE} {TIME_RANGE}",
        "Any {EVENT_TYPE} {TIME_RANGE}?",
        "Pull all {EVENT_TYPE} from {TIME_RANGE}",
        "What happened {TIME_RANGE} regarding {EVENT_TYPE}?"
    ],
    "filter_followup": [
        "Filter only from IP {SOURCE_IP}",
        "Only show attempts from {SOURCE_IP}",
        "Filter by {SEVERITY} severity",
        "Show only {SEVERITY} alerts",
        "Narrow it down to {SEVERITY} events",
        "Exclude IP {SOURCE_IP}",
        "Just show me logs for user {USER_ACCOUNT}"
    ],
    "generate_report": [
        "Generate a summary of attacks {TIME_RANGE}",
        "Create a {TIME_RANGE} attack report with charts",
        "Give me a {TIME_RANGE} {EVENT_TYPE} summary",
        "Generate security summary for {TIME_RANGE}",
        "Compile a report on {ATTACK_TYPE} for {TIME_RANGE}",
        "Export the {EVENT_TYPE} dashboard for {TIME_RANGE}"
    ],
    "count_aggregate": [
        "How many {ATTACK_TYPE} attacks happened {TIME_RANGE}",
        "Count total {ATTACK_TYPE} attempts {TIME_RANGE}",
        "Total number of {EVENT_TYPE} {TIME_RANGE}",
        "What is the total count of {SEVERITY} alerts {TIME_RANGE}",
        "Give me the numbers for {EVENT_TYPE} {TIME_RANGE}"
    ],
    "incident_investigation": [
        "Show all requests from {SOURCE_IP} {TIME_RANGE}",
        "What did user {USER_ACCOUNT} do {TIME_RANGE}?",
        "Trace all activity for {USER_ACCOUNT} {TIME_RANGE}",
        "Did {SOURCE_IP} trigger any {SEVERITY} alerts {TIME_RANGE}?",
        "Show full network flow for {SOURCE_IP} {TIME_RANGE}"
    ]
}

dataset = []

for intent, phrases in templates.items():
    for phrase in phrases:
        for _ in range(15):
            text = phrase
            entities = {}
            if "{ATTACK_TYPE}" in text:
                val = random.choice(attack_types)
                text = text.replace("{ATTACK_TYPE}", val)
                entities["ATTACK_TYPE"] = val
            if "{TIME_RANGE}" in text:
                val = random.choice(time_ranges)
                text = text.replace("{TIME_RANGE}", val)
                entities["TIME_RANGE"] = val
            if "{EVENT_TYPE}" in text:
                val = random.choice(event_types)
                text = text.replace("{EVENT_TYPE}", val)
                entities["EVENT_TYPE"] = val
            if "{SEVERITY}" in text:
                val = random.choice(severities)
                text = text.replace("{SEVERITY}", val)
                entities["SEVERITY"] = val
            if "{SOURCE_IP}" in text:
                val = random.choice(ips)
                text = text.replace("{SOURCE_IP}", val)
                entities["SOURCE_IP"] = val
            if "{USER_ACCOUNT}" in text:
                val = random.choice(user_accounts)
                text = text.replace("{USER_ACCOUNT}", val)
                entities["USER_ACCOUNT"] = val
            data_point = {"text": text, "intent": intent, "entities": entities}
            if data_point not in dataset:
                dataset.append(data_point)

clarification_intents = [
    {"text": "What do you mean by unusual activity", "intent": "clarify_needed", "entities": {}},
    {"text": "I am not sure what to search for", "intent": "clarify_needed", "entities": {}},
    {"text": "Can you help me find something suspicious", "intent": "clarify_needed", "entities": {}},
    {"text": "What kind of queries can I ask", "intent": "clarify_needed", "entities": {}},
    {"text": "Help me investigate this incident", "intent": "clarify_needed", "entities": {}},
    {"text": "I dont understand what to look for", "intent": "clarify_needed", "entities": {}},
    {"text": "What is the difference between XSS and IDOR", "intent": "clarify_needed", "entities": {}},
    {"text": "How do I start an investigation", "intent": "clarify_needed", "entities": {}},
    {"text": "Can you explain what a brute force attack is", "intent": "clarify_needed", "entities": {}},
    {"text": "What should I check first", "intent": "clarify_needed", "entities": {}},
    {"text": "I need guidance on where to start", "intent": "clarify_needed", "entities": {}},
    {"text": "What does this alert mean", "intent": "clarify_needed", "entities": {}},
    {"text": "How do I filter results", "intent": "clarify_needed", "entities": {}},
    {"text": "What information do you need from me", "intent": "clarify_needed", "entities": {}},
    {"text": "Can you show me an example query", "intent": "clarify_needed", "entities": {}}
]
dataset.extend(clarification_intents)

random.shuffle(dataset)

with open("training_data_large.json", "w") as f:
    json.dump(dataset, f, indent=2)

print(f"Successfully generated {len(dataset)} records!")

intent_counts = {}
for ex in dataset:
    intent = ex["intent"]
    intent_counts[intent] = intent_counts.get(intent, 0) + 1

print("\nExamples per intent:")
for intent, count in intent_counts.items():
    print(f"  {intent}: {count}")
