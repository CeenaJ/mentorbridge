import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv('/Users/ceenaj/mentorbridge/backend/.env')

nebius_llm = ChatOpenAI(
    base_url=os.getenv('NEBIUS_BASE_URL'),
    api_key=os.getenv('NEBIUS_API_KEY'),
    model=os.getenv('MODEL_NAME'),
    temperature=0.7,
    max_tokens=200
)

def profile_agent(state: dict) -> dict:
    profile = state["student_profile"]
    prompt = f"""Summarise this student profile in 2 concise sentences for mentor matching.
Name: {profile.get("name")}
Field: {profile.get("field")}
Target University: {profile.get("target_university")}
Goals: {profile.get("goals")}
Achievements: {profile.get("achievements")}
"""
    response = nebius_llm.invoke(prompt)
    state["student_profile"]["summary"] = response.content
    print(f"Profile Agent: {response.content}")
    return state
