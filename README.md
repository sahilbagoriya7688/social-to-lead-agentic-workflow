# Social-to-Lead Agentic Workflow

A GenAI-powered conversational agent built for the ServiceHive Machine Learning Internship Assignment.

## Overview

This project implements a **Social-to-Lead Agentic Workflow** — an intelligent conversational AI agent for **Inflix**, a fictional AI-powered social media automation SaaS product. The agent:

- Answers product questions using **RAG** (Retrieval-Augmented Generation)
- Detects user **intent** (browsing / curious / interested / high-intent / ready-to-buy)
- Automatically **captures leads** when high-intent users are identified
- Executes **tools** like lead saving, calendar booking, and pricing lookup
- Powered by **Google Gemini 1.5 Flash** (FREE API)

## Architecture

```
User Input
    │
    ▼
┌─────────────────────────────────┐
│         Agent Orchestrator      │
│  (intent detection + routing)   │
└────────────┬────────────────────┘
             │
    ┌────────┴────────┐
    ▼                 ▼
RAG Engine       Tool Executor
(Product Q&A)    (Lead Capture /
                  Booking / Pricing)
    │                 │
    └────────┬────────┘
             ▼
      Response Generator
        (Gemini API)
```

## Project Structure

```
social-to-lead-agentic-workflow/
├── agent/
│   ├── __init__.py
│   ├── orchestrator.py       # Main agent loop
│   ├── intent_detector.py    # Intent classification (Gemini)
│   └── response_generator.py # Response formatting (Gemini)
├── rag/
│   ├── __init__.py
│   └── retriever.py          # RAG retrieval logic
├── tools/
│   ├── __init__.py
│   ├── lead_capture.py       # Lead saving tool
│   ├── pricing_tool.py       # Pricing lookup tool
│   └── booking_tool.py       # Demo booking tool
├── data/
│   ├── product_docs.json     # Product knowledge base
│   └── leads.json            # Captured leads storage
├── main.py                   # CLI entry point
├── app.py                    # Streamlit web UI
├── requirements.txt
├── .env.example
└── README.md
```

## Features

### 1. Intent Detection (5 Levels)
| Level | Description | Example |
|---|---|---|
| BROWSING | Just exploring | "hi", "hello" |
| CURIOUS | General questions | "what does Inflix do?" |
| INTERESTED | Feature/pricing interest | "how much does it cost?" |
| HIGH_INTENT | Actively evaluating | "I want to try it" |
| READY_TO_BUY | Ready to sign up | "I want to sign up now" |

### 2. RAG-Powered Product Q&A
Uses vector-based retrieval over Inflix product documentation (features, pricing, integrations, onboarding).

### 3. Tool Execution
| Intent Level | Tool Triggered |
|---|---|
| HIGH_INTENT | Lead Capture |
| READY_TO_BUY | Lead Capture + Demo Booking |
| INTERESTED | Pricing Lookup |

### 4. Lead Management
Captured leads stored with name, email, company, intent, and timestamp.

## Setup

### Prerequisites
- Python 3.9+
- **Google Gemini API key** (FREE at [aistudio.google.com](https://aistudio.google.com))

### Installation

```bash
git clone https://github.com/sahilbagoriya7688/social-to-lead-agentic-workflow.git
cd social-to-lead-agentic-workflow
pip install -r requirements.txt
```

### Get Free Gemini API Key

1. Go to **https://aistudio.google.com**
2. Sign in with your Google account
3. Click **"Get API Key"** → **"Create API key"**
4. Copy the key (starts with `AIza...`)

### Configuration

```bash
cp .env.example .env
# Edit .env and add your Gemini API key:
# GEMINI_API_KEY=your-key-here
```

### Run CLI Agent

```bash
python main.py
```

### Run Web UI (Streamlit)

```bash
streamlit run app.py
```

## Example Conversation

```
You: What does Inflix do?
Agent: Inflix is an AI-powered social media automation platform...
[Intent: CURIOUS]

You: How much does it cost?
Agent: Inflix offers three plans: Starter ($29/mo), Growth ($79/mo)...
[Intent: INTERESTED] → Pricing tool invoked

You: I want to try it for my startup
Agent: That's great! Could I get your name to get you started?
[Intent: HIGH_INTENT] → Lead capture initiated

You: Sahil
Agent: Nice to meet you, Sahil! What's your email address?

You: sahil@example.com
Agent: Thanks! And what company are you from?

You: TechStartup
Agent: 🎉 Lead captured! Our team will reach out within 24 hours.
✅ Lead Successfully Captured!
```

## Tech Stack

- **Python 3.9+**
- **Google Gemini 1.5 Flash** (LLM — FREE)
- **LangChain** (RAG framework)
- **FAISS** (vector store)
- **Streamlit** (web UI)
- **Pydantic** (data validation)

## Assignment Context

Built for the ServiceHive Machine Learning Intern technical assignment:
- **Company:** ServiceHive
- **Role:** Machine Learning Intern (GenAI Engineer)
- **Assignment:** Social-to-Lead Agentic Workflow
- **Product:** Inflix — AI-powered social media automation SaaS

## Author

**Sahil Bagoriya**
- GitHub: [@sahilbagoriya7688](https://github.com/sahilbagoriya7688)
