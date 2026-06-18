# MentorBridge 🎓
### by Ceena Justin

An AI-powered mentorship platform connecting students aged 14-17 
with university alumni and current students in their creative field.

## What it does
Students get matched to mentors in Film, Music, Art, Writing, 
Engineering or Medicine using a multi-agent AI system built with 
LangGraph and powered by Nebius LLM.

## Tech Stack
- **LangGraph** — Multi-agent state machine (3 agents)
- **LangChain** — LLM integration
- **Nebius** — LLM provider (Llama 3.3 70B)
- **FastAPI** — Backend API
- **SQLite** — Database
- **LangSmith** — Agent tracing and observability
- **HTML/CSS/JS** — Frontend

## Agents
1. **Profile Agent** — Summarises student profile for matching
2. **Matching Agent** — Finds best mentor using AI
3. **Session Agent** — Facilitates mentorship conversation as mentor persona

## How to run
```bash
cd backend
pip install -r requirements.txt
python main.py
```

## Week 3 Project — Mastering Agentic AI Bootcamp
The Gen Academy 
