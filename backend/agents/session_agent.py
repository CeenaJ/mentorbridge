import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv("/Users/ceenaj/mentorbridge/backend/.env")

nebius_llm = ChatOpenAI(
    base_url=os.getenv("NEBIUS_BASE_URL"),
    api_key=os.getenv("NEBIUS_API_KEY"),
    model=os.getenv("MODEL_NAME"),
    temperature=0.7,
    max_tokens=300
)

def session_agent(state):
    mentor = state["selected_mentor"]
    messages = state.get("session_messages", [])
    system_prompt = "You are " + mentor["name"] + ", a " + mentor["year"] + " at " + mentor["university"] + " studying " + mentor["field"] + ". Bio: " + mentor["bio"] + ". You are mentoring a student. Be warm, specific, and helpful. Keep responses under 150 words."
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    response = nebius_llm.invoke(full_messages)
    messages.append({"role": "assistant", "content": response.content})
    state["session_messages"] = messages
    print("Session Agent: " + response.content)
    return state
