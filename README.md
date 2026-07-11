# SIEM Assistant — Conversational Security Investigation Platform

> An NLP-powered SIEM interface that lets SOC analysts investigate 
> security threats in plain English — no query syntax required.

## Demo
[Add your LinkedIn video link here]

## Architecture
- **Phase 1**: Real attack execution (XSS/IDOR via Burp Suite on OWASP Juice Shop)
- **Phase 2**: Nginx reverse proxy logging
- **Phase 3**: Custom Python detector (regex + sequential IDOR pattern detection)
- **Phase 4**: NLP Pipeline (DistilBERT + Logistic Regression, 97% accuracy)
- **Backend**: FastAPI REST API
- **Frontend**: React (Bloomberg-style professional UI)

## Features
- Natural language to Elasticsearch DSL translation
- Multi-turn context-aware conversations
- Real-time XSS and IDOR detection
- Visual report generation (charts + tables)
- Plain English explanation of WHY alerts were flagged
- Live sidebar with recent detections

## Tech Stack
| Component | Technology |
|---|---|
| Attack Simulation | Burp Suite + OWASP Juice Shop |
| Log Capture | Nginx reverse proxy |
| Detection Engine | Custom Python (regex + sequential pattern) |
| Storage | Elasticsearch 8.x |
| NLP Model | DistilBERT embeddings + Logistic Regression |
| Backend | FastAPI + Python |
| Frontend | React + Recharts |

## Setup
```bash
# start clowning
git clone https://github.com/senvidit4-alt/siem-assistant

# Docker start 
cd siem-assistant
sudo docker-compose up -d
sudo docker start elasticsearch

# Backend start k
source venv/bin/activate
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Frontend start k
cd frontend
npm start
```

## Project Story
Built this after months of manual threat hunting with 
Zeek logs and grep/awk pipelines. Knew exactly what 
analysts ask during investigations — built the tool 
that translates those questions into SIEM queries automatically.

## Author
B.Tech AI-DS Student | Cybersecurity Enthusiast
GitHub: senvidit4-alt
