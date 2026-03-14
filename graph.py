import os
import streamlit as st
from typing import TypedDict, List, Dict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI

# Securely pull the API key for Cloud Deployment
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", temperature=0.1)

class TutoringState(TypedDict):
    problem_statement: str
    extracted_concepts: List[str]
    current_concept_index: int
    mastery_scores: Dict[str, float]
    current_exercise: str
    student_response: Optional[str]
    feedback: str
    phase: str

def get_clean_text(ai_content) -> str:
    """Forces LangChain's dictionary outputs into plain, readable text."""
    if isinstance(ai_content, str):
        return ai_content
    elif isinstance(ai_content, list):
        if len(ai_content) > 0 and isinstance(ai_content[0], dict):
            return ai_content[0].get("text", str(ai_content))
        return "".join(str(x) for x in ai_content)
    return str(ai_content)

def concept_extractor_agent(state: TutoringState) -> Dict:
    problem = state["problem_statement"]
    prompt = f"Analyze this problem: '{problem}'. Extract the 2 most fundamental concepts needed to solve it. Return ONLY a comma-separated list of the 2 concepts. No other text."
    
    raw_response = llm.invoke(prompt).content
    clean_text = get_clean_text(raw_response) 
    
    concepts = [c.strip() for c in clean_text.split(",") if c.strip()]
    if not concepts: concepts = ["Understanding the Question", "Solving the Equation"]
        
    return {
        "extracted_concepts": concepts,
        "current_concept_index": 0,
        "mastery_scores": {c: 0.1 for c in concepts},
        "phase": "Extraction Complete"
    }

def teaching_agent(state: TutoringState) -> Dict:
    current_idx = state.get("current_concept_index", 0)
    concepts = state.get("extracted_concepts", [])
    
    if current_idx >= len(concepts):
        return {"current_exercise": "All concepts mastered!", "phase": "Complete"}
        
    concept = concepts[current_idx]
    problem = state["problem_statement"]
    
    prompt = f"""
    You are an expert tutor. The student wants to solve this problem: '{problem}'.
    Before they solve it, teach them the foundational concept of: '{concept}'.
    Provide:
    1. A brief 2-sentence explanation of the concept.
    2. A short, relevant example with different numbers.
    3. End by asking the student to apply this concept to their original problem.
    """
    
    raw_response = llm.invoke(prompt).content
    clean_text = get_clean_text(raw_response) 
    
    return {"current_exercise": clean_text, "phase": f"Teaching: {concept}"}

def evaluation_agent(state: TutoringState) -> Dict:
    current_idx = state.get("current_concept_index", 0)
    concepts = state.get("extracted_concepts", [])
    
    if current_idx >= len(concepts):
        return {
            "feedback": "You've finished this session! Click '🔄 Start New Problem' in the sidebar to tackle a new challenge.",
            "phase": "Session Complete",
            "student_response": None
        }
        
    concept = concepts[current_idx]
    student_answer = state.get("student_response", "").lower()
    problem = state.get("problem_statement", "")
    exercise_asked = state.get("current_exercise", "")
    scores = state.get("mastery_scores", {}).copy()
    
    # --- 1. The Bypass Valve Logic ---
    if "understand" in student_answer or "yes" in student_answer or "got it" in student_answer:
        scores[concept] = 1.0
        new_index = current_idx + 1
        
        # FEATURE ADDITION: Generate Practice problems if they finish the final concept
        if new_index >= len(concepts):
            practice_prompt = f"The student just mastered the concepts to solve this problem: '{problem}'. Generate 3 similar practice problems with different numbers. Format nicely with bullet points. Start your response with '🎉 **Problem Complete!** To solidify your knowledge, try these 3 practice exercises on your own:'"
            practice_text = get_clean_text(llm.invoke(practice_prompt).content)
            feedback = f"🌟 **Great work!**\n\n---\n\n{practice_text}"
        else:
            feedback = "🌟 **Great! Let's move on to the next step.**"
            
        return {
            "feedback": feedback,
            "current_concept_index": new_index,
            "mastery_scores": scores,
            "student_response": None,
            "phase": "Evaluation Complete"
        }
        
    # --- 2. The Grading Logic ---
    prompt = f"""
    You are evaluating a student. Original problem: '{problem}'. Concept: '{concept}'. Question asked: '{exercise_asked}'. Student's Answer: '{student_answer}'.
    Is the student's answer mathematically correct? 
    If yes, start your response with EXACTLY the word "CORRECT" followed by brief, encouraging feedback.
    If no, start your response with EXACTLY the word "INCORRECT" followed by the step-by-step mathematical solution so they can learn from it. End by asking them to type 'I understand'.
    """
    
    raw_response = llm.invoke(prompt).content
    clean_text = get_clean_text(raw_response) 
    upper_text = clean_text.upper() 
    
    if "CORRECT" in upper_text and "INCORRECT" not in upper_text:
        feedback = clean_text[upper_text.find("CORRECT")+7:].replace(":**", "").replace(":", "").strip()
        scores[concept] = 1.0
        new_index = current_idx + 1
        
        # FEATURE ADDITION: Generate Practice problems if they answer the final concept correctly
        if new_index >= len(concepts):
            practice_prompt = f"The student just mastered the concepts to solve this problem: '{problem}'. Generate 3 similar practice problems with different numbers. Format nicely with bullet points. Start your response with '🎉 **Problem Complete!** To solidify your knowledge, try these 3 practice exercises on your own:'"
            practice_text = get_clean_text(llm.invoke(practice_prompt).content)
            feedback = f"{feedback}\n\n---\n\n{practice_text}"
            
    else:
        feedback = clean_text[upper_text.find("INCORRECT")+9:].replace(":**", "").replace(":", "").strip()
        scores[concept] = 0.5
        new_index = current_idx
        
    return {
        "feedback": feedback,
        "current_concept_index": new_index,
        "mastery_scores": scores,
        "student_response": None,
        "phase": "Evaluation Complete"
    }

def entry_router(state: TutoringState) -> str:
    if not state.get("extracted_concepts"): return "extract"
    return "evaluate"

def pedagogical_router(state: TutoringState) -> str:
    if state.get("current_concept_index", 0) >= len(state.get("extracted_concepts", [])):
        return "end"
        
    current_idx = state["current_concept_index"]
    concept = state["extracted_concepts"][current_idx]
    
    if state["mastery_scores"].get(concept) == 0.5:
        return "end"
    else:
        return "teach"

builder = StateGraph(TutoringState)
builder.add_node("extract", concept_extractor_agent)
builder.add_node("teach", teaching_agent)
builder.add_node("evaluate", evaluation_agent)

builder.add_conditional_edges(START, entry_router, {"extract": "extract", "evaluate": "evaluate"})
builder.add_edge("extract", "teach")
builder.add_edge("teach", END)
builder.add_conditional_edges("evaluate", pedagogical_router, {"teach": "teach", "end": END})