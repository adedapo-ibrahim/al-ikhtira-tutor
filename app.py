import streamlit as st
import uuid
from langgraph.checkpoint.memory import MemorySaver
from graph import builder 

st.set_page_config(page_title="AL-IKHTIRA Tutor", page_icon="logo.png", layout="wide")

st.title("🏫 AL-IKHTIRA Intelligent Tutoring System")
st.markdown("##### *NextGen Adaptive Scaffolding for Secondary School Education*")
st.divider()

@st.cache_resource
def get_tutor_graph():
    memory = MemorySaver()
    return builder.compile(checkpointer=memory)

tutor_graph = get_tutor_graph()

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
config = {"configurable": {"thread_id": st.session_state.thread_id}}

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome! Paste any Math, Physics, or Chemistry problem, and we will break it down step-by-step."}]

current_graph_state = tutor_graph.get_state(config)
state_values = current_graph_state.values if current_graph_state else {}
mastery_scores = state_values.get("mastery_scores", {})

with st.sidebar:
    # UPDATED: Modern Streamlit syntax for stretching the logo
    st.image("logo.png", width="stretch") 
    st.divider()
    
    st.header("📊 Student Diagnostic Model")
    
    # UPDATED: Modern Streamlit syntax for stretching the button
    if st.button("🔄 Start New Problem", width="stretch"): 
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = [{"role": "assistant", "content": "Memory cleared! Paste a new problem to begin."}]
        st.rerun()
    st.divider()

    st.info(state_values.get("phase", "Awaiting Problem"))
    st.markdown("**Concept Mastery Probabilities:**")
    if mastery_scores:
        for concept, score in mastery_scores.items():
            st.progress(float(score), text=f"{concept}: {int(score * 100)}%")
    else:
        st.write("Submit a school problem to initialize tracking.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("Enter your problem..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        if not state_values.get("extracted_concepts"):
            inputs = {"problem_statement": user_input}
        else:
            inputs = {"student_response": user_input}
            
            # Check for bypass valve directly from user input here just in case
            if any(word in user_input.lower() for word in ["understand", "got it", "yes"]):
                 st.session_state.messages.append({"role": "assistant", "content": "🌟 **Great! Let's move on.**"})

        final_output = ""
        for output in tutor_graph.stream(inputs, config):
            for node_name, node_state in output.items():
                
                if node_name == "evaluate" and "feedback" in node_state:
                    final_output += f"{node_state['feedback']}\n\n"
                    
                if node_name == "teach" and "current_exercise" in node_state:
                    final_output += f"{node_state['current_exercise']}"

        message_placeholder.markdown(final_output)
        st.session_state.messages.append({"role": "assistant", "content": final_output})
    st.rerun()
