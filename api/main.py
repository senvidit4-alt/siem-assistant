from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import sys
import re
from typing import Dict, Any
from datetime import datetime

sys.path.append("/home/kali/siem-assistant/nlp")

from sentence_transformers import SentenceTransformer
from query_generator import generate_query
from siem_connector import fetch_alerts, format_results, generate_explanation
from intent_resolver import resolve_intent_with_llm

app = FastAPI(title="Advanced SIEM Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

print("[*] Loading NLP models...")
try:
    sentence_model = SentenceTransformer("/home/kali/siem-assistant/nlp/sentence_transformer_model")
    with open("/home/kali/siem-assistant/nlp/intent_classifier.pkl", "rb") as f:
        intent_classifier = pickle.load(f)
    print("[*] Models loaded successfully!")
except Exception as e:
    print(f"[!] Error loading models: {e}")

class ContextManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def update_context(self, session_id: str, intent: str, entities: dict):
        if session_id not in self.sessions:
            self.sessions[session_id] = {"last_intent": None, "merged_entities": {}, "last_updated": None}
        current_entities = self.sessions[session_id]["merged_entities"]
        for key, value in entities.items():
            current_entities[key] = value
        self.sessions[session_id]["last_intent"] = intent
        self.sessions[session_id]["last_updated"] = datetime.now()

    def get_merged_entities(self, session_id: str, new_entities: dict) -> dict:
        if session_id not in self.sessions:
            return new_entities
        merged = self.sessions[session_id]["merged_entities"].copy()
        for key, value in new_entities.items():
            merged[key] = value
        return merged

    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

context_manager = ContextManager()

def extract_entities(text: str) -> dict:
    entities = {}
    text_lower = text.lower()

    attack_map = {
        r"\bxss\b": "XSS",
        r"cross site": "XSS",
        r"\bidor\b": "IDOR",
        r"insecure direct": "IDOR",
        r"\bsqli\b": "SQLi",
        r"sql injection": "SQLi",
        r"brute force": "Brute Force",
        r"\bddos\b": "DDoS",
        r"\brce\b": "RCE",
        r"\bcsrf\b": "CSRF",
        r"phishing": "Phishing",
        r"ai.mutated|obfuscat|bypass|entropy|waf|evasion|fuzzer": "AI_MUTATED_XSS"
    }
    for pattern, val in attack_map.items():
        if re.search(pattern, text_lower):
            entities["ATTACK_TYPE"] = val
            break

    time_map = {
        r"today": "today",
        r"yesterday": "yesterday",
        r"last hour": "last hour",
        r"last 24 hours": "last 24 hours",
        r"this week": "this week",
        r"last week": "last week",
        r"this month": "this month",
        r"last month": "last month",
        r"last night": "last night",
        r"past 15 minutes": "past 15 minutes"
    }
    for pattern, val in time_map.items():
        if re.search(pattern, text_lower):
            entities["TIME_RANGE"] = val
            break

    ip_match = re.search(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b', text)
    if ip_match:
        entities["SOURCE_IP"] = ip_match.group(1)

    for sev in ["critical", "high", "medium", "low"]:
        if re.search(rf"\b{sev}\b", text_lower):
            entities["SEVERITY"] = sev
            break

    return entities

class QueryRequest(BaseModel):
    text: str
    session_id: str = "default"

class ClearRequest(BaseModel):
    session_id: str = "default"

@app.get("/")
def root():
    return {"status": "ok", "message": "Advanced SIEM Assistant Core is Online."}

@app.post("/query")
def process_query(request: QueryRequest):
    try:
        # Step 1: Intent classify karo
        embedding = sentence_model.encode([request.text])
        intent = intent_classifier.predict(embedding)[0]
        confidence = float(intent_classifier.predict_proba(embedding).max())

        # Step 2: Agar confidence kam hai — Ollama se resolve karo
        if confidence < 0.45 or intent == "clarify_needed":
            print(f"[*] Low confidence ({confidence:.2f}), asking Ollama...")
            intent, confidence = resolve_intent_with_llm(request.text)
            print(f"[*] Ollama resolved: {intent} ({confidence:.2f})")

        # Step 3: Agar abhi bhi clarify needed
        if intent == "clarify_needed" or confidence < 0.30:
            return {
                "intent": intent,
                "confidence": round(confidence, 2),
                "type": "clarification",
                "explanation": "I'm not completely sure what you need. Could you rephrase? (e.g., 'Show me XSS attempts today' or 'Did any AI attacks bypass WAF today?')"
            }

        # Step 4: Entity extraction
        entities = extract_entities(request.text)
        merged_entities = context_manager.get_merged_entities(request.session_id, entities)

        # Step 5: Advanced threat hunting handling
        if intent == "advanced_threat_hunting":
            merged_entities["ATTACK_TYPE"] = "AI_MUTATED_XSS"
            intent = "web_attack_analysis"
            confidence = 0.90

        # Step 6: Filter without base search check
        if intent == "filter_followup" and not merged_entities.get("TIME_RANGE"):
            return {
                "intent": intent,
                "confidence": round(confidence, 2),
                "type": "clarification",
                "explanation": "You asked to filter, but I don't know what we are filtering. Please start with a base search like 'Show me all alerts today'."
            }

        # Step 7: Query generate karo
        query = generate_query(intent, merged_entities)

        # Step 8: Elasticsearch fetch karo
        try:
            response = fetch_alerts(query)
            result = format_results(response, intent)
            explanation = generate_explanation(result, intent, merged_entities)
        except Exception as e:
            result = {"error": "Failed to connect to SIEM/Elasticsearch backend."}
            explanation = str(e)

        # Step 9: Context update karo
        context_manager.update_context(request.session_id, intent, entities)

        return {
            "intent": intent,
            "confidence": round(confidence, 2),
            "entities_found_in_text": entities,
            "context_used_for_query": merged_entities,
            "query_dsl": query,
            "result": result,
            "explanation": explanation,
            "type": result.get("type", "alerts") if isinstance(result, dict) else "unknown"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/clear")
def clear_session(request: ClearRequest):
    context_manager.clear_session(request.session_id)
    return {"message": f"Context memory for session '{request.session_id}' has been cleared."}

@app.get("/alerts/recent")
def get_recent_alerts():
    query = {
        "query": {"match_all": {}},
        "sort": [{"@timestamp": {"order": "desc"}}],
        "size": 10
    }
    response = fetch_alerts(query)
    result = format_results(response, "search_logs")
    return result
