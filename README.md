    # ⏰ Reminder Agent

    An autonomous natural-language scheduling workspace built with **Streamlit**, the **Google GenAI SDK**, and **Pydantic**. The Reminder Agent parses user scheduling intent, calculates execution target dates and times, and registers active background thread timers with a real-time sidebar control panel.

    ---

    ## ✨ Features

    * **Natural Language Intent Parsing**: Translates human relative time commands (e.g., *"Remind me to submit team report in 10 minutes"*) into absolute timestamps using Gemini 2.5 Flash.
    * **Structured Output Schema**: Enforces strict JSON data structures via `Pydantic` models.
    * **Resilient Background Execution**: Uses Python's native `threading` engine with headless cloud fallbacks so notifications log safely on remote Linux servers.
    * **Live Operations Dashboard**: Dynamic 1-second ticks showing active task countdowns, one-click `+5m Snooze`, task cancellation, and chime sound alerts.
    * **Cross-Browser Theme Fixes**: Custom CSS rules designed to maintain high contrast and visible UI controls across Chrome and Edge browser dark/light mode filters.

    ---

    ## 🚀 Quick Start (Local Setup)

    ### 1. Prerequisites

    Ensure Python 3.10 or higher is installed on your local machine.

    ### 2. Clone the Repository

    ```bash
    git clone https://github.com/YOUR_USERNAME/reminder-agent.git
    cd reminder-agent
    ```

    ### 3. Set Up Virtual Environment & Dependencies

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
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