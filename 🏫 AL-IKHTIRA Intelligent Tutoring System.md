# **🏫 AL-IKHTIRA Intelligent Tutoring System**

**AL-IKHTIRA** is a NextGen Adaptive Scaffolding platform for Secondary Education. Built for the 3MTT NextGen Knowledge Showcase, it uses a multi-agent AI architecture to act as a true pedagogical tutor that breaks down problems, teaches concepts, and evaluates math step-by-step, rather than just giving away the final answer.

## **🚀 Features**

* **Dynamic Concept Extraction:** Automatically reads a student's problem (Math, Physics, Chemistry) and builds a custom curriculum.  
* **Stateful Memory:** Uses LangGraph to remember the exact state of the student's learning journey.  
* **Live Diagnostic Model:** A sidebar UI that visually tracks the student's mastery probability for each concept.  
* **Intelligent Evaluation:** Grades math dynamically, catches errors, and provides step-by-step mathematical solutions to guide the student back on track.

## **🛠️ Installation & Setup**

**Clone the repository**  
git clone \[https://github.com/yourusername/al-ikhtira-tutor.git\](https://github.com/yourusername/al-ikhtira-tutor.git)  
cd al-ikhtira-tutor

1. 

**Install Dependencies**  
pip install streamlit langgraph langchain-google-genai

2.   
3. **Add your API Key.** Open `graph.py` and replace `"PASTE_YOUR_API_KEY_HERE"` with your actual Google Gemini API key.

**Run the Application**  
python \-m streamlit run app.py

4. 

## **🧠 Architecture**

This system bypasses standard LLM wrappers by utilizing a **LangGraph State Machine**.

* `app.py`: Handles the Streamlit frontend, chat history, and UI state.  
* `graph.py`: Houses the cognitive engine. It includes an Entry Router, a Concept Extractor Agent, a Teaching Agent, an Evaluation Agent, and a Pedagogical Router to loop the student until 100% mastery is achieved.

