# 🚀 DevPro: AI-Driven Self-Healing Infrastructure

An autonomic, AI-powered system designed to predict, detect, and automatically resolve silent server infrastructure failures and containerized anomalies within 2 seconds using Large Language Models (LLMs), Live Retrieval-Augmented Generation (RAG), and Docker automation.

---

## 👥 DevPro Team & Roles
* **Maryam Salah** — Team Leader & AI Developer 🧠
* **Omar Fadalla** — Backend & Metrics Engineer 💻
* **Homam DevOps** — Infrastructure & Docker Automation ⚙️
* **Sarah Zoghly** — Frontend & UI Dashboard Developer 🎨

---

## 🛠️ System Architecture & Data Flow

```text
 [1. Backend Metrics] ──> [2. AI Agent Loop] ──> [3. Automated Remediation] ──> [4. UI Dashboard]
 (Omar: CPU at 95.8%)    (Maryam: RAG Check)     (Homam: Docker Restart)        (Sarah: Live Monitor)
```

1. **Metrics Collection (Input):** The system polls real-time server telemetry parameters (CPU/RAM metrics) utilizing native runtime hooks.
2. **AI Intelligence Engine:** If anomalies cross the predefined threshold (>85%), the AI Agent interprets real-time logs against the enterprise static documentation library via RAG.
3. **Automated Recovery (Output):** The agent generates structured JSON execution tasks payload, automatically firing containment remediation procedures (`docker restart`) to restore full operational integrity.
4. **Visual Telemetry Monitoring:** Telemetry changes and self-healing lifecycle loops are broadcasted to the frontend UI dashboard using operational color states.

---

## 📥 Project Layout
* `app.py` — Core Python Orchestrator, AI Engine loop, and Docker integration.
* `knowledge.txt` — The Retrieval-Augmented Generation (RAG) enterprise engineering library.

---
*Built with passion by Team DevPro for the DevOps Hackathon 2026.*
