  # ⏰ Reminder Agent

An autonomous natural-language scheduling workspace built with **Streamlit**, the **Google GenAI SDK**, and **Pydantic**. The Reminder Agent parses user scheduling intent, calculates execution target dates and times, and registers active background thread timers with a real-time sidebar control panel.

🌐 **Live Demo**: [https://reminder-agent-001.streamlit.app/](https://reminder-agent-001.streamlit.app/)

---

## ✨ Features

* **Natural Language Intent Parsing**: Translates human relative time commands (e.g., *"Remind me to submit team report in 10 minutes"*) into absolute timestamps using Gemini 2.5/3.5 models.
* **Function Tool Calling**: Uses Gemini structured tool execution (`create_reminder_tool`, `update_reminder_tool`) to schedule and modify tasks dynamically.
* **Multi-Model Fallback Engine**: Built with automated fallback models (`gemini-2.5-flash`, `gemini-2.5-flash-lite`, `gemini-3.5-flash-lite`) to bypass API load limits.
* **Resilient Background Execution**: Uses Python's native `threading` engine with desktop OS (`plyer`) and non-intrusive Web Audio API sound alerts.
* **Live Operations Dashboard**: Dynamic 1-second ticks showing active task countdowns, one-click `+5m Snooze`, task cancellation, and bottom-anchored dashboard clearing.

---

## 🚀 Quick Start (Local Setup)

### 1. Prerequisites

Ensure Python 3.10 or higher is installed on your local machine.

### 2. Clone the Repository

```bash
git clone [https://github.com/Roy709/reminder_agent.git](https://github.com/Roy709/reminder_agent.git)
cd reminder_agent

    ### 3. Set Up Virtual Environment & Dependencies

    ```bash
    python -m venv venv

    # macOS / Linux:
    source venv/bin/activate  

    # Windows (Command Prompt / PowerShell):
     venv\Scripts\activate
    pip install -r requirements.txt
    ```

    ### 4. Set Up Environment Variables

    Create a `.env` file in the root directory:

    ```
    GEMINI_API_KEY=your_actual_gemini_api_key_here
    ```

    ### 5. Launch the Application

    ```bash
    streamlit run app.py
