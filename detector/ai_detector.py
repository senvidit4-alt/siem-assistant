import re
import math
import time
import os
from datetime import datetime
from collections import defaultdict
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")
LOG_FILE = "/home/kali/siem-assistant/logs/access.log"

def calculate_entropy(text):
    if not text:
        return 0
    freq = defaultdict(int)
    for c in text:
        freq[c] += 1
    length = len(text)
    entropy = -sum(
        (count/length) * math.log2(count/length)
        for count in freq.values()
    )
    return entropy

OBFUSCATION_PATTERNS = [
    r"%[0-9a-fA-F]{2}%[0-9a-fA-F]{2}%[0-9a-fA-F]{2}",
    r"&#x[0-9a-fA-F]+;",
    r"\\u[0-9a-fA-F]{4}",
    r"(%3C|%3E|%22|%27){3,}",
]

XSS_PATTERNS = [
    r"<script", r"<iframe", r"javascript:",
    r"onerror=", r"onload=", r"alert\(",
    r"%3Cscript", r"%3Ciframe",
]

idor_tracker = defaultdict(list)
IDOR_THRESHOLD = 3

def parse_log_line(line):
    # Flexible pattern — bytes ke baad optional fields
    pattern = r'(\S+) - - \[([^\]]+)\] "(\S+) (\S+)[^"]*" (\d+) (\d+)'
    match = re.match(pattern, line)
    if match:
        return {
            "source_ip": match.group(1),
            "timestamp": match.group(2),
            "method": match.group(3),
            "url": match.group(4),
            "status": int(match.group(5)),
            "bytes": int(match.group(6))
        }
    return None

def detect_ai_mutated(parsed):
    url = parsed["url"]
    entropy = calculate_entropy(url)
    high_entropy = entropy > 3.8
    obfuscation_found = any(re.search(p, url, re.IGNORECASE) for p in OBFUSCATION_PATTERNS)
    has_xss = any(re.search(p, url, re.IGNORECASE) for p in XSS_PATTERNS)
    if (high_entropy and has_xss) or obfuscation_found:
        return True, {"entropy": round(entropy, 2), "obfuscation_found": obfuscation_found}
    return False, None

def detect_xss(parsed):
    url = parsed["url"].lower()
    for pattern in XSS_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return True, pattern
    return False, None

def detect_idor(parsed):
    url = parsed["url"]
    ip = parsed["source_ip"]
    match = re.search(r"/api/(Users|Orders|Feedback)/(\d+)", url, re.IGNORECASE)
    if match:
        endpoint = match.group(1)
        user_id = int(match.group(2))
        key = f"{ip}_{endpoint}"
        idor_tracker[key].append(user_id)
        recent = idor_tracker[key][-10:]
        if len(recent) >= IDOR_THRESHOLD:
            sorted_recent = sorted(recent[-IDOR_THRESHOLD:])
            is_sequential = all(
                sorted_recent[i] + 1 == sorted_recent[i+1]
                for i in range(len(sorted_recent)-1)
            )
            if is_sequential:
                return True, {"type": "sequential", "ids": recent}
        if len(recent) >= 5:
            return True, {"type": "high_frequency", "ids": recent, "endpoint": endpoint}
    return False, None

def create_alert(alert_type, parsed, extra_info=None, description=None):
    alert = {
        "@timestamp": datetime.utcnow().isoformat(),
        "rule": {
            "type": alert_type,
            "group": alert_type.lower(),
            "id": "100500" if alert_type == "AI_MUTATED_XSS" else "100100"
        },
        "source_ip": parsed["source_ip"],
        "url": parsed["url"],
        "method": parsed["method"],
        "status_code": parsed["status"],
        "description": description or f"{alert_type} detected",
        "extra_info": str(extra_info) if extra_info else ""
    }
    result = es.index(index="siem-alerts", document=alert)
    print(f"[ALERT] {alert_type} from {parsed['source_ip']}")
    print(f"        URL: {parsed['url'][:80]}")
    print(f"        ID: {result['_id']}")

def watch_log():
    print("[*] AI-Enhanced SIEM Detector starting...")
    print(f"[*] Watching: {LOG_FILE}")
    print("[*] Detecting: XSS, IDOR, AI_MUTATED_XSS")
    print("[*] Waiting for new logs...")
    print("-" * 60)

    current_size = os.path.getsize(LOG_FILE)

    with open(LOG_FILE, "r") as f:
        f.seek(current_size)

        while True:
            new_size = os.path.getsize(LOG_FILE)

            if new_size > current_size:
                lines = f.readlines()
                current_size = new_size

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    parsed = parse_log_line(line)
                    if not parsed:
                        print(f"[!] Parse failed: {line[:80]}")
                        continue

                    is_ai, ai_info = detect_ai_mutated(parsed)
                    if is_ai:
                        create_alert("AI_MUTATED_XSS", parsed, ai_info,
                            f"Suspected AI-Mutated payload. Entropy: {ai_info['entropy']}")
                        continue

                    is_xss, pattern = detect_xss(parsed)
                    if is_xss:
                        create_alert("XSS", parsed, pattern, f"XSS pattern: {pattern}")
                        continue

                    is_idor, ids = detect_idor(parsed)
                    if is_idor:
                        create_alert("IDOR", parsed, ids, f"Sequential IDOR: {ids}")

            time.sleep(0.3)

if __name__ == "__main__":
    watch_log()
