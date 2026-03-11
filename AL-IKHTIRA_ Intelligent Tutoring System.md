# **AL-IKHTIRA: Intelligent Tutoring System**

**3MTT NextGen Knowledge Showcase** **Creator:** Adedapo Ibrahim Bayo

### **1\. The Problem**

The current landscape of digital education and AI adoption is fundamentally flawed. When secondary school students face difficult STEM problems, standard AI chatbots (like ChatGPT or standard Gemini) simply provide the final answer. This encourages short-term memorization and cheating rather than genuine comprehension. There is a massive shortage of human tutors in Nigeria capable of providing the one-on-one "scaffolding" and breaking a problem down, teaching the core concept, and testing the student, required for true mastery.

### **2\. The Users**

* **Primary Users:** Secondary school students (specifically in STEM subjects like Math, Physics, and Chemistry) who need personalized, step-by-step academic support outside of classroom hours.  
* **Secondary Users:** Educators and schools seeking to provide automated, high-quality remedial tutoring without exhausting human resources.

### **3\. The Build (Architecture)**

AL-IKHTIRA is not a standard prompt-wrapper; it is a sophisticated Multi-Agent State Machine.

* **Frontend:** Built with Streamlit to provide a clean, accessible chat interface and live diagnostic tracking.  
* **Backend State Management:** Powered by LangGraph with memory checkpointing (MemorySaver). This allows the system to remember where the student is in their learning journey, rather than treating every message as a new prompt.  
* **Cognitive Engine:** Powered by the Google Gemini 3.0 Flash API. The architecture utilizes specific routing agents:  
  * *Concept Extractor:* Dynamically reads the user's problem and builds a localized curriculum.  
  * *Pedagogical Teacher:* Generates custom micro-lessons and examples.  
  * *Mathematical Evaluator:* Grades student inputs, provides step-by-step corrections, and controls the flow of the state machine based on a live Mastery Score.

### **4\. The Impact**

AL-IKHTIRA transitions EdTech from "Automated Answering" to "Automated Teaching." By forcing students to prove their reasoning and calculate step-by-step solutions when they fail, the platform mimics the patience and pedagogical strategy of an expert human tutor. This democratizes elite, one-on-one tutoring for any student with internet access, fundamentally raising the ceiling for STEM comprehension in Nigeria.

### **5\. Scalability**

The architecture is inherently highly scalable. Because it relies on an API-driven LLM (Gemini 3.0 Flash) rather than local compute, it can handle thousands of concurrent students. The LangGraph state machine is strictly defined, meaning we can easily scale the curriculum to include subjects beyond STEM (like History or Literature) simply by adjusting the Concept Extractor agent, without rewriting the core application logic.

