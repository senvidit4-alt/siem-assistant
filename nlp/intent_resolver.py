import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"

# Fast keyword fallback — Ollama se pehle check hoga
KEYWORD_INTENT_MAP = {
    "advanced_threat_hunting": [
        "waf", "bypass", "evad", "obfuscat", "mutated", "fuzzer",
        "entropy", "encoded attack", "passed the", "got through",
        "slipped through", "got past", "ai attack", "llm", "evasion",
        "double encod", "hex encod", "unicode escap", "filter bypass",
        "passed waf", "bypassed", "got past", "snuck through"
    ],
    "web_attack_analysis": [
        "xss", "idor", "sqli", "sql injection", "cross site",
        "script inject", "object reference", "injection attack"
    ],
    "generate_report": [
        "report", "summary", "chart", "graph", "overview",
        "compile", "generate", "weekly", "monthly"
    ],
    "count_aggregate": [
        "how many", "count", "total", "number of", "how much"
    ],
    "search_logs": [
        "failed login", "authentication", "suspicious login",
        "brute force", "malware", "show logs", "show alerts"
    ],
    "incident_investigation": [
        "trace", "investigate", "activity from", "what did", "track"
    ]
}

def keyword_fallback(text: str):
    """Fast keyword-based intent detection — no LLM needed"""
    text_lower = text.lower()
    for intent, keywords in KEYWORD_INTENT_MAP.items():
        for kw in keywords:
            if kw in text_lower:
                return intent, 0.85
    return None, 0.0

INTENT_DESCRIPTIONS = {
    "web_attack_analysis": "searching for XSS, IDOR, SQLi, or any web attack alerts",
    "search_logs": "searching security logs for events like failed logins",
    "filter_followup": "filtering previous results by IP, severity, or criteria",
    "generate_report": "generating a summary report or chart",
    "count_aggregate": "counting total numbers of attacks or alerts",
    "incident_investigation": "investigating a specific IP address or user activity",
    "advanced_threat_hunting": "finding AI-generated attacks, WAF bypass, obfuscated payloads",
    "clarify_needed": "query is too vague to understand"
}

def resolve_intent_with_llm(user_query: str) -> tuple:
    """
    Step 1: Fast keyword check
    Step 2: Ollama fallback (agar keyword match nahi hua)
    """
    # Fast path — keyword check pehle
    intent, confidence = keyword_fallback(user_query)
    if intent:
        print(f"[*] Keyword match: {intent} ({confidence})")
        return intent, confidence

    # Slow path — Ollama
    print(f"[*] No keyword match, trying Ollama...")
    prompt = f"""Classify this security query into exactly one intent.

Query: "{user_query}"

Intents:
- advanced_threat_hunting: WAF bypass, obfuscated payloads, AI attacks, evasion
- web_attack_analysis: XSS, IDOR, SQLi, injection attacks
- search_logs: failed logins, malware, suspicious activity
- filter_followup: filter by IP, severity, narrow down results
- generate_report: create summary, chart, report
- count_aggregate: count total, how many
- incident_investigation: trace activity, investigate IP
- clarify_needed: unclear query

Return ONLY this JSON, nothing else:
{{"intent": "intent_name", "confidence": 0.85}}"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 50}
            },
            timeout=60
        )

        if response.status_code == 200:
            text = response.json().get("response", "").strip()
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                result = json.loads(text[start:end])
                intent = result.get("intent", "clarify_needed")
                confidence = float(result.get("confidence", 0.5))
                if intent not in INTENT_DESCRIPTIONS:
                    intent = "clarify_needed"
                return intent, confidence

    except Exception as e:
        print(f"[!] Ollama failed: {e}")

    return "clarify_needed", 0.3
