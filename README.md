# Social-to-Lead Agentic Workflow

A GenAI-powered conversational agent built for the ServiceHive Machine Learning Internship Assignment.

## Overview

This project implements a **Social-to-Lead Agentic Workflow** — an intelligent conversational AI agent for **Inflix**, a fictional AI-powered social media automation SaaS product. The agent:

- Answers product questions using **RAG** (Retrieval-Augmented Generation)
- Detects user **intent** (curious / interested / high-intent / ready-to-buy)
- Automatically **captures leads** when high-intent users are identified
- Executes **tools** like lead saving, calendar booking, and pricing lookup

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
```

## Project Structure

```
social-to-lead-agentic-workflow/
├── agent/
│   ├── __init__.py
│   ├── orchestrator.py       # Main agent loop
│   ├── intent_detector.py    # Intent classification
│   └── response_generator.py # Response formatting
├── rag/
│   ├── __init__.py
│   ├── knowledge_base.py     # Product knowledge base
│   └── retriever.py          # RAG retrieval logic
├── tools/
│   ├── __init__.py
│   ├── lead_capture.py       # Lead saving tool
│   ├── pricing_tool.py       # Pricing lookup tool
│   └── booking_tool.py       # Demo booking tool
├── data/
│   ├── product_docs.json     # Product knowledge base docs
│   └── leads.json            # Captured leads storage
├── main.py                   # Entry point (CLI chat)
├── app.py                    # Streamlit web UI
├── requirements.txt
├── .env.example
└── README.md
```

## Features

### 1. Intent Detection
The agent classifies each user message into one of 5 intent levels:
- `BROWSING` — Just exploring, no specific interest
- `CURIOUS` — Asking general questions about the product
- `INTERESTED` — Showing genuine interest, asking about features/pricing
- `HIGH_INTENT` — Actively evaluating, asking about trials/demos
- `READY_TO_BUY` — Ready to sign up or purchase

### 2. RAG-Powered Product Q&A
Uses a vector-based retrieval system over Inflix product documentation to answer:
- Feature questions
- Pricing inquiries
- Integration questions
- Use case examples

### 3. Tool Execution
Based on intent level, the agent automatically invokes tools:
| Intent Level | Tool Triggered |
|---|---|
| HIGH_INTENT | Lead Capture |
| READY_TO_BUY | Lead Capture + Demo Booking |
| INTERESTED | Pricing Lookup |

### 4. Lead Management
Captured leads are stored with:
- Name, email, company
- Detected intent level
- Conversation summary
- Timestamp

## Setup

### Prerequisites
- Python 3.9+
- OpenAI API key (or compatible LLM)

### Installation

```bash
git clone https://github.com/sahilbagoriya7688/social-to-lead-agentic-workflow.git
cd social-to-lead-agentic-workflow
pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Run CLI Agent

```bash
python main.py
```

### Run Web UI

```bash
streamlit run app.py
```

## Example Conversation

```
You: What does Inflix do?
Agent: Inflix is an AI-powered social media automation platform that helps businesses 
       schedule posts, analyze engagement, and auto-generate content using AI...

[Intent: CURIOUS]

You: How much does it cost?
Agent: Inflix offers three plans: Starter ($29/mo), Growth ($79/mo), and Enterprise 
       (custom pricing). Would you like to see a detailed feature comparison?

[Intent: INTERESTED] → Pricing tool invoked

You: I want to try it out for my startup
Agent: That's great! I'd love to set up a personalized demo for you. 
       Could I get your name and email to get you started?

[Intent: HIGH_INTENT] → Lead capture tool invoked
✅ Lead captured and saved!
```

## Tech Stack

- **Python 3.9+**
- **OpenAI GPT-4o** (LLM backbone)
- **LangChain** (agent framework + RAG)
- **FAISS** (vector store for RAG)
- **Streamlit** (web UI)
- **Pydantic** (data validation)

## Assignment Context

Built as part of the ServiceHive Machine Learning Intern technical assignment:
- **Company:** ServiceHive
- **Role:** Machine Learning Intern (GenAI Engineer)
- **Product:** Inflix — AI-powered social media automation SaaS

## Author

**Sahil Bagoriya**
- GitHub: [@sahilbagoriya7688](https://github.com/sahilbagoriya7688)
