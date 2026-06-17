import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from agents.profile_agent import profile_agent
from agents.matching_agent import matching_agent
from agents.session_agent import session_agent

class MentorBridgeState(TypedDict):
    student_profile: dict
    mentor_candidates: list
    selected_mentor: dict
    session_messages: list
    session_complete: bool
    action_plan: str

def should_continue_session(state):
    if state.get("session_complete", False):
        return "end"
    return "session_agent"

def build_graph():
    workflow = StateGraph(MentorBridgeState)
    workflow.add_node("profile_agent", profile_agent)
    workflow.add_node("matching_agent", matching_agent)
    workflow.add_node("session_agent", session_agent)
    workflow.set_entry_point("profile_agent")
    workflow.add_edge("profile_agent", "matching_agent")
    workflow.add_edge("matching_agent", END)
    return workflow.compile()

graph = build_graph()

def run_matching(student_profile):
    state = {
        "student_profile": student_profile,
        "mentor_candidates": [],
        "selected_mentor": {},
        "session_messages": [],
        "session_complete": False,
        "action_plan": ""
    }
    result = graph.invoke(state)
    return result
