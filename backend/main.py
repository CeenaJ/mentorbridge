from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from graph.mentor_graph import run_matching
from agents.session_agent import session_agent
from database import (register_student, login_student, get_student,
                      save_session, save_message, get_student_sessions,
                      get_session_messages, save_story, get_stories,
                      update_action_plan, init_db)
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

init_db()

class StudentRegister(BaseModel):
    name: str
    email: str
    password: str
    field: str
    target_university: str
    goals: str
    achievements: str

class StudentLogin(BaseModel):
    email: str
    password: str

class MatchRequest(BaseModel):
    student_id: Optional[int] = None
    name: str
    field: str
    target_university: str
    goals: str
    achievements: str

class ChatMessage(BaseModel):
    student_id: Optional[int] = None
    session_id: Optional[int] = None
    mentor_id: int
    mentor_name: str
    mentor_university: str
    mentor_field: str
    mentor_year: str
    mentor_bio: str
    message: str
    history: list

class NewSession(BaseModel):
    student_id: int
    mentor_id: int
    mentor_name: str
    mentor_university: str
    mentor_field: str

class StoryPost(BaseModel):
    student_id: int
    student_name: str
    field: str
    content: str

class ActionPlanRequest(BaseModel):
    session_id: int
    history: list
    mentor_name: str

@app.get("/")
def root():
    return {"status": "MentorBridge API running"}

@app.post("/register")
def register(data: StudentRegister):
    result = register_student(data.name, data.email, data.password,
                              data.field, data.target_university,
                              data.goals, data.achievements)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    s = result["student"]
    return {"success": True, "student": {"id": s["id"], "name": s["name"],
            "email": s["email"], "field": s["field"],
            "target_university": s["target_university"],
            "goals": s["goals"], "achievements": s["achievements"]}}

@app.post("/login")
def login(data: StudentLogin):
    result = login_student(data.email, data.password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    s = result["student"]
    return {"success": True, "student": {"id": s["id"], "name": s["name"],
            "email": s["email"], "field": s["field"],
            "target_university": s["target_university"],
            "goals": s["goals"], "achievements": s["achievements"]}}

@app.get("/student/{student_id}")
def get_student_profile(student_id: int):
    student = get_student(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.get("/student/{student_id}/sessions")
def get_sessions(student_id: int):
    return {"sessions": get_student_sessions(student_id)}

@app.get("/session/{session_id}/messages")
def get_messages(session_id: int):
    return {"messages": get_session_messages(session_id)}

@app.post("/match")
def match_student(profile: MatchRequest):
    result = run_matching(profile.dict())
    return {"mentors": result["mentor_candidates"]}

@app.post("/session/start")
def start_session(data: NewSession):
    session_id = save_session(data.student_id, data.mentor_id,
                              data.mentor_name, data.mentor_university,
                              data.mentor_field)
    return {"session_id": session_id}

@app.post("/chat")
def chat(data: ChatMessage):
    state = {
        "selected_mentor": {
            "id": data.mentor_id,
            "name": data.mentor_name,
            "university": data.mentor_university,
            "field": data.mentor_field,
            "year": data.mentor_year,
            "bio": data.mentor_bio
        },
        "session_messages": data.history + [{"role": "user", "content": data.message}],
        "session_complete": False
    }
    result = session_agent(state)
    reply = result["session_messages"][-1]["content"]
    if data.session_id:
        save_message(data.session_id, "user", data.message)
        save_message(data.session_id, "assistant", reply)
    return {"response": reply, "history": result["session_messages"]}

@app.post("/session/action-plan")
def generate_action_plan(data: ActionPlanRequest):
    from agents.profile_agent import nebius_llm
    history_text = "\n".join([f"{m["role"]}: {m["content"]}" for m in data.history])
    prompt = f"""Based on this mentorship conversation with {data.mentor_name}, 
    generate a clear action plan with 5 specific steps the student should take.
    Format as numbered list. Be specific and actionable.
    
    Conversation:
    {history_text}"""
    response = nebius_llm.invoke(prompt)
    if data.session_id:
        update_action_plan(data.session_id, response.content)
    return {"action_plan": response.content}

@app.post("/stories")
def post_story(data: StoryPost):
    save_story(data.student_id, data.student_name, data.field, data.content)
    return {"success": True}

@app.get("/stories")
def list_stories():
    return {"stories": get_stories()}


class MentorRegister(BaseModel):
    name: str
    email: str
    password: str
    field: str
    university: str
    year: str
    bio: str
    linkedin: str = ""

@app.post("/mentor/register")
def mentor_register(data: MentorRegister):
    from database import register_mentor
    result = register_mentor(data.name, data.email, data.password,
                             data.field, data.university, data.year,
                             data.bio, data.linkedin)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    m = result["mentor"]
    return {"success": True, "mentor": {"id": m["id"], "name": m["name"],
            "field": m["field"], "university": m["university"],
            "year": m["year"], "bio": m["bio"]}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
