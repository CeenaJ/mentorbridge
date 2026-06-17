import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv("/Users/ceenaj/mentorbridge/backend/.env")

nebius_llm = ChatOpenAI(base_url=os.getenv("NEBIUS_BASE_URL"), api_key=os.getenv("NEBIUS_API_KEY"), model=os.getenv("MODEL_NAME"), temperature=0.3, max_tokens=200)

MENTORS = [
    {"id": 1, "name": "Maya Chen", "university": "Brown University", "field": "Film", "year": "Alumni", "bio": "Film director, graduated 2022, worked on 3 short films at Sundance"},
    {"id": 2, "name": "James Wilson", "university": "NYU Tisch", "field": "Film", "year": "Current Student", "bio": "3rd year film student, specialising in documentary and narrative film"},
    {"id": 3, "name": "Priya Patel", "university": "Royal College of Art", "field": "Visual Art", "year": "Alumni", "bio": "Visual artist and illustrator, exhibited in London and New York"},
    {"id": 4, "name": "David Kim", "university": "Berklee College of Music", "field": "Music", "year": "Alumni", "bio": "Music producer and composer, worked with major labels"},
    {"id": 5, "name": "Sophie Brown", "university": "Brown University", "field": "Music", "year": "Current Student", "bio": "4th year music student, pianist and composer"}
]

def matching_agent(state):
    student_summary = state["student_profile"].get("summary", "")
    student_field = state["student_profile"].get("field", "")
    student_university = state["student_profile"].get("target_university", "")
    mentor_list = ", ".join([str(m["id"]) + ":" + m["name"] + "-" + m["field"] + "-" + m["university"] for m in MENTORS])
    prompt = "Match this student: " + student_summary + ". University: " + student_university + ". Field: " + student_field + ". Mentors: " + mentor_list + ". Reply ONLY: MATCHES: 1,2,3"
    response = nebius_llm.invoke(prompt)
    try:
        ids_text = response.content.split("MATCHES:")[1].strip()
        ids = [int(x.strip()) for x in ids_text.split(",")[:3]]
        matched_mentors = [m for m in MENTORS if m["id"] in ids]
    except:
        matched_mentors = MENTORS[:3]
    state["mentor_candidates"] = matched_mentors
    print("Matching Agent found " + str(len(matched_mentors)) + " mentors")
    return state
