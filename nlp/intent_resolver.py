import re
import difflib

# Known security terms dictionary
SECURITY_TERMS = [
    "xss", "idor", "sqli", "sql injection", "brute force", "csrf", "rce", "ddos", "phishing",
    "attack", "attacks", "bypass", "waf", "evasion", "obfuscated", "mutated", "fuzzer",
    "report", "summary", "chart", "filter", "show", "give", "list", "display",
    "today", "yesterday", "week", "month", "hour", "night",
    "how many", "count", "total", "any", "all", "recent",
    "investigate", "trace", "activity", "incident",
    "malware", "login", "authentication", "alert", "alerts", "logs",
]

def normalize_query(text: str) -> str:
    """
    2-step normalization:
    1. Repeated chars compress (xxsss → xs, attaack → atack)
    2. Word-level fuzzy match against known security terms
    """
    text_lower = text.lower()

    # Step 1: Compress repeated chars
    compressed = re.sub(r'(.)\1{2,}', r'\1\1', text_lower)

    # Step 2: Word-level fuzzy correction
    words = compressed.split()
    corrected = []
    for word in words:
        # Skip short words and numbers
        if len(word) <= 2 or word.isdigit():
            corrected.append(word)
            continue

        # Find closest match
        matches = difflib.get_close_matches(word, SECURITY_TERMS, n=1, cutoff=0.75)
        if matches:
            corrected.append(matches[0])
        else:
            corrected.append(word)

    result = " ".join(corrected)
    if result != text_lower:
        print(f"[*] Normalized: '{text_lower}' → '{result}'")
    return result

KEYWORD_INTENT_MAP = [
    ("advanced_threat_hunting", [
        "waf", "bypass", "evasion", "obfuscated", "mutated", "fuzzer",
        "entropy", "got through", "slipped through", "got past",
        "ai attack", "filter bypass", "passed waf", "bypassed",
        "ai generated", "encoded attack",
    ]),
    ("count_aggregate", [
        "how many", "count", "total", "how much", "number of", "tally"
    ]),
    ("generate_report", [
        "report", "summary", "chart", "graph", "overview",
        "statistics", "stats", "breakdown", "trend", "compile"
    ]),
    ("filter_followup", [
        "filter", "only show", "narrow down", "exclude",
        "just show", "limit to", "refine", "from ip", "by ip",
        "only from", "restrict"
    ]),
    ("incident_investigation", [
        "trace", "investigate", "full activity", "drill down",
        "all activity from", "what did", "track", "history"
    ]),
    ("web_attack_analysis", [
        "xss", "idor", "sqli", "sql injection", "cross site",
        "brute force", "rce", "csrf", "phishing", "ddos",
        "attack", "attacks", "malicious", "payload", "injection",
        "exploit", "vulnerability", "hack", "intrusion", "threat"
    ]),
    ("search_logs", [
        "show all", "give me all", "list all", "all alerts",
        "all events", "what happened", "show everything",
        "any alerts", "recent", "show logs", "all logs",
        "failed login", "authentication", "suspicious", "malware",
        "show", "give", "display", "fetch", "get", "any", "all"
    ]),
]

TIME_PATTERNS = {
    "today": ["today", "aaj", "this day", "right now", "current"],
    "yesterday": ["yesterday", "kal", "last day", "previous day"],
    "this week": ["this week", "week", "7 days", "past week"],
    "last week": ["last week", "previous week"],
    "this month": ["this month", "month", "30 days"],
    "last 24 hours": ["24 hours", "last 24", "past 24"],
    "last hour": ["last hour", "past hour", "1 hour"],
    "last night": ["last night", "overnight", "night"],
}

ATTACK_PATTERNS = {
    "XSS": ["xss", "cross site", "script", "scripting"],
    "IDOR": ["idor", "insecure direct", "object reference"],
    "SQLi": ["sqli", "sql injection", "sql"],
    "Brute Force": ["brute force", "brute", "password spray"],
    "AI_MUTATED_XSS": ["waf bypass", "bypass", "obfuscated", "mutated", "fuzzer", "ai attack"],
}

def extract_time_from_text(text: str) -> str:
    text_lower = text.lower()
    for time_val, keywords in TIME_PATTERNS.items():
        if any(kw in text_lower for kw in keywords):
            return time_val
    return "today"

def extract_attack_from_text(text: str) -> str:
    text_lower = text.lower()
    for attack, keywords in ATTACK_PATTERNS.items():
        if any(kw in text_lower for kw in keywords):
            return attack
    return ""

def extract_ip_from_text(text: str) -> str:
    match = re.search(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b', text)
    return match.group(1) if match else ""

def resolve_intent_with_llm(user_query: str) -> tuple:
    """
    Step 1: Normalize query (typo fix via difflib)
    Step 2: Keyword intent match
    Step 3: Default fallback
    """
    normalized = normalize_query(user_query)

    for intent, keywords in KEYWORD_INTENT_MAP:
        if any(kw in normalized for kw in keywords):
            print(f"[*] Intent: {intent} | Query: '{normalized}'")
            return intent, 0.85

    print(f"[*] No match — default: search_logs")
    return "search_logs", 0.65
