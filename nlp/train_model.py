import json
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

print("[*] Loading dataset...")
with open("dataset/training_data_large.json", "r") as f:
    data = json.load(f)

texts = [d["text"] for d in data]
labels = [d["intent"] for d in data]

print(f"[*] Total examples: {len(texts)}")
print(f"[*] Intents: {set(labels)}")

print("\n[*] Loading DistilBERT model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("[*] Generating embeddings (this may take 1-2 minutes)...")
embeddings = model.encode(texts, show_progress_bar=True)
print(f"[*] Embeddings shape: {embeddings.shape}")

X_train, X_test, y_train, y_test = train_test_split(
    embeddings, labels, test_size=0.2, random_state=42, stratify=labels
)

print(f"\n[*] Training set: {len(X_train)} examples")
print(f"[*] Test set: {len(X_test)} examples")

print("\n[*] Training Logistic Regression classifier...")
classifier = LogisticRegression(max_iter=1000, random_state=42)
classifier.fit(X_train, y_train)

print("\n[*] Evaluating model...")
y_pred = classifier.predict(X_test)
print(classification_report(y_test, y_pred))

print("[*] Saving model...")
with open("intent_classifier.pkl", "wb") as f:
    pickle.dump(classifier, f)

model.save("sentence_transformer_model")

print("\n✅ Training complete!")
print("   Saved: intent_classifier.pkl")
print("   Saved: sentence_transformer_model/")

def predict_intent(text):
    embedding = model.encode([text])
    intent = classifier.predict(embedding)[0]
    confidence = classifier.predict_proba(embedding).max()
    return intent, confidence

print("\n[*] Quick test:")
test_queries = [
    "Show me XSS attempts today",
    "Generate weekly attack report",
    "Filter only from IP 192.168.1.10",
    "How many IDOR attacks this week",
    "Show all requests from that IP yesterday",
    "What do you mean by unusual activity"
]

for query in test_queries:
    intent, conf = predict_intent(query)
    print(f"  '{query}'")
    print(f"   → {intent} (confidence: {conf:.2f})")
    print()
