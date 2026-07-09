import re
import time
from datetime import datetime
from collections import defaultdict
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

LOG_FILE = "/home/kali/siem-assistant/logs/access.log"

XSS_PATTERNS = [
    r"<script",
    r"<iframe",
    r"javascript:",
    r"onerror=",
    r"onload=",
    r"alert\(",
    r"%3Cscript",
    r"%3Ciframe",
    r"%22javascript",
]

idor_tracker = defaultdict(list)
IDOR_THRESHOLD = 3

def parse_log_line(line):
    pattern = r'(\S+) - - \[([^\]]+)\] "(\S+) (\S+) ([^"]+)" (\d+) (\d+)'
    match = re.match(pattern, line)
    if match:
        return {
            "source_ip": match.group(1),
            "timestamp": match.group(2),
            "method": match.group(3),
            "url": match.group(4),
            "status": int(match.group(6)),
            "bytes": int(match.group(7))
        }
    return None

def detect_xss(parsed):
    url = parsed["url"].lower()
    for pattern in XSS_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return True, pattern
    return False, None

def detect_idor(parsed):
    url = parsed["url"]
    ip = parsed["source_ip"]
    match = re.search(r"/api/Users/(\d+)", url, re.IGNORECASE)
    if match:
        user_id = int(match.group(1))
        idor_tracker[ip].append(user_id)
        recent = idor_tracker[ip][-10:]
        if len(recent) >= IDOR_THRESHOLD:
            sorted_recent = sorted(recent[-IDOR_THRESHOLD:])
            is_sequential = all(
                sorted_recent[i] + 1 == sorted_recent[i+1]
                for i in range(len(sorted_recent)-1)
            )
            if is_sequential:
                return True, recent
    return False, None

def get_description(alert_type, extra_info):
    if alert_type == "XSS":
        return f"XSS attempt detected. Suspicious pattern '{extra_info}' found in request URL."
    elif alert_type == "IDOR":
        return f"Possible IDOR attack. Sequential user IDs accessed: {extra_info}"
    return "Unknown attack type detected."

def create_alert(alert_type, parsed, extra_info=None):
    alert = {
        "@timestamp": datetime.utcnow().isoformat(),
        "rule": {
            "type": alert_type,
            "group": alert_type.lower(),
        },
        "source_ip": parsed["source_ip"],
        "url": parsed["url"],
        "method": parsed["method"],
        "status_code": parsed["status"],
        "description": get_description(alert_type, extra_info),
        "extra_info": str(extra_info) if extra_info else ""
    }
    result = es.index(index="siem-alerts", document=alert)
    print(f"[ALERT] {alert_type} detected from {parsed['source_ip']} → {parsed['url']}")
    print(f"        Stored in Elasticsearch: {result['_id']}")
    return alert

def watch_log():
    print("[*] Starting SIEM Detector...")
    print(f"[*] Watching: {LOG_FILE}")
    print("[*] Elasticsearch: http://localhost:9200")
    print("[*] Index: siem-alerts")
    print("-" * 50)
    with open(LOG_FILE, "r") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            line = line.strip()
            if not line:
                continue
            parsed = parse_log_line(line)
            if not parsed:
                continue
            is_xss, pattern = detect_xss(parsed)
            if is_xss:
                create_alert("XSS", parsed, pattern)
                continue
            is_idor, ids = detect_idor(parsed)
            if is_idor:
                create_alert("IDOR", parsed, ids)

if __name__ == "__main__":
    if not es.indices.exists(index="siem-alerts"):
        es.indices.create(
            index="siem-alerts",
            mappings={
                "properties": {
                    "@timestamp": {"type": "date"},
                    "rule.type": {"type": "keyword"},
                    "rule.group": {"type": "keyword"},
                    "source_ip": {"type": "keyword"},
                    "url": {"type": "text"},
                    "description": {"type": "text"},
                }
            }
        )
        print("[*] Created 'siem-alerts' index in Elasticsearch")
    watch_log()
