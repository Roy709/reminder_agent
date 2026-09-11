import streamlit as st
import threading
from datetime import datetime, timedelta
from plyer import notification
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Setup
st.set_page_config(
    page_title="Reminder Agent",
    page_icon="⏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------
# 1. Cross-Browser CSS Styling System (Chrome & Edge Dark Mode Override)
# -------------------------------------------------------------------
st.markdown("""
<style>
    /* Global Page Body Reset */
    .stApp {
        background-color: #f8fafc !important;
        color: #0f172a !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Force Light Theme Colors on Chat Messages Across All Browsers */
    [data-testid="stChatMessage"], 
    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] span,
    .stChatMessage [data-testid="stMarkdownContainer"] p {
        color: #0f172a !important;
        font-weight: 500 !important;
    }

    /* Force Sidebar Open Toggle Button (>>) Visible Across Chrome & Edge Dark Themes */
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        position: fixed !important;
        top: 0.5rem !important;
        left: 0.5rem !important;
        z-index: 999999 !important;
        background-color: #1e1b4b !important; /* Dark indigo matching Hero Banner */
        border-radius: 8px !important;
        border: 1px solid #312e81 !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15) !important;
        padding: 4px !important;
    }
    
    /* Force SVG Arrow Paths Pure White Regardless of OS Theme */
    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="stSidebarCollapsedControl"] button *,
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] path {
        color: #ffffff !important;
        fill: #ffffff !important;
        stroke: #ffffff !important;
        opacity: 1 !important;
        visibility: visible !important;
    }

    [data-testid="stSidebarCollapsedControl"]:hover {
        background-color: #312e81 !important;
    }

    /* Sidebar Base Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
        color: #1e293b !important;
    }
    [data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #475569 !important;
    }

    /* Reduce Header Padding & Margin */
    [data-testid="stHeader"] {
        height: 0px !important;
        min-height: 0px !important;
        background-color: transparent !important;
        z-index: 100 !important;
    }
    
    /* Hide Deploy Button & Main Menu */
    .stAppDeployButton, #MainMenu {
        display: none !important;
    }

    /* Reduce Main Block Container Top Padding */
    .main .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 950px;
    }

    /* Sidebar Width Configuration */
    [data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 360px !important;
        max-width: 360px !important;
    }

    /* Pure White Floating Bottom Chat Input Box Override */
    [data-testid="stBottom"], [data-testid="stBottom"] > div {
        background-color: #f8fafc !important;
    }
    [data-testid="stChatInput"], 
    [data-testid="stChatInput"] > div, 
    [data-baseweb="base-input"], 
    [data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 12px !important;
    }
    [data-testid="stChatInput"] * {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #64748b !important;
    }

    /* Hero Banner Component */
    .hero-container {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        padding: 20px 24px;
        border-radius: 12px;
        color: white !important;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .hero-title {
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0;
        color: #ffffff !important;
    }
    .hero-subtitle {
        font-size: 0.9rem;
        color: #c7d2fe !important;
        margin-top: 4px;
    }

    /* Custom Non-Wrapping Status Badges */
    .status-badge-active {
        background-color: #dcfce7 !important;
        color: #15803d !important;
        font-size: 0.75rem;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        display: inline-block;
        white-space: nowrap;
    }

    .status-badge-triggered {
        background-color: #e0e7ff !important;
        color: #4338ca !important;
        font-size: 0.75rem;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        display: inline-block;
        white-space: nowrap;
    }

    /* Live Agent Pulse Status */
    .agent-status-bar {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 16px;
        background-color: #ffffff;
        padding: 8px 14px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    .status-pulse {
        height: 10px;
        width: 10px;
        background-color: #22c55e;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
        animation: pulse-green 2s infinite;
    }
    @keyframes pulse-green {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(34, 197, 94, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 2. State Management & Memory Initialization
# -------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your **Reminder Agent**. Tell me what you'd like to be reminded about and when, and I will set precision timers for you."}
    ]

if "reminders" not in st.session_state:
    st.session_state.reminders = []

if "timers" not in st.session_state:
    st.session_state.timers = {}

def get_gemini_chat_history():
    history = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        history.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))
    return history

# -------------------------------------------------------------------
# 3. Notification & Scheduling Logic (plyer + datetime + threading)
# -------------------------------------------------------------------
def trigger_notification(task_name: str):
    """Fires native OS desktop notification with cloud server fallback."""
    try:
        notification.notify(
            title="⏰ Reminder Agent Alert",
            message=task_name,
            app_name="Reminder Agent",
            timeout=10
        )
    except Exception as e:
        print(f"Cloud execution alert triggered for task: '{task_name}' (Desktop notification skipped on server: {e})")

def create_reminder_tool(task: str, scheduled_time: str) -> str:
    """Schedules a new task with active thread references."""
    try:
        target_dt = datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M:%S")
        delay = (target_dt - datetime.now()).total_seconds()
        task_id = f"task_{int(datetime.now().timestamp())}"

        if delay > 0:
            timer = threading.Timer(delay, trigger_notification, args=[task])
            timer.start()
            st.session_state.timers[task_id] = timer
            status = "Active"
        else:
            trigger_notification(task)
            status = "Triggered"

        st.session_state.reminders.append({
            "id": task_id,
            "task": task,
            "scheduled_time": scheduled_time,
            "target_dt": target_dt,
            "status": status,
            "created_at": datetime.now().strftime("%H:%M:%S")
        })
        return f"SUCCESS: Scheduled reminder '{task}' for {scheduled_time}."
    except Exception as e:
        return f"ERROR: Failed to parse execution time - {str(e)}"

# Function Tool Declaration
reminder_tool_decl = types.FunctionDeclaration(
    name="create_reminder_tool",
    description="Schedules a reminder task to run at an absolute timestamp (YYYY-MM-DD HH:MM:SS format).",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "task": types.Schema(type=types.Type.STRING, description="Description of the task or reminder."),
            "scheduled_time": types.Schema(type=types.Type.STRING, description="Target datetime string (YYYY-MM-DD HH:MM:SS)."),
        },
        required=["task", "scheduled_time"],
    ),
)

tools_config = types.Tool(function_declarations=[reminder_tool_decl])

# -------------------------------------------------------------------
# 4. Core Agent Reasoning Engine with Fallback Handling
# -------------------------------------------------------------------
def run_agent_turn():
    client = genai.Client()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    system_instruction = (
        f"You are the Reminder Agent, an autonomous scheduling assistant. Current system timestamp: {now_str}.\n\n"
        "CORE RESPONSIBILITIES:\n"
        "1. Schedule tasks precision-calculated relative to current system timestamp.\n"
        "2. PARAMETER GATHERING: If the prompt lacks exact details (e.g., missing date/time or reminder description), "
        "do not attempt tool execution. Respectfully request missing fields.\n"
        "3. DOMAIN BOUNDARIES: Reject off-topic general knowledge/trivia requests politely. Focus strictly on reminders and task scheduling.\n"
        "4. Call `create_reminder_tool` immediately when parameters are resolved."
    )

    chat_contents = get_gemini_chat_history()

    # Valid model endpoints prevent 503 UNAVAILABLE crashes on Render/Streamlit Cloud
    models_to_try = ["gemini-3.5-flash-lite", "gemini-3.5-flash"]
    response = None

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=chat_contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    tools=[tools_config],
                    temperature=0.1
                )
            )
            break
        except Exception as e:
            print(f"Model {model_name} failed: {e}. Attempting fallback...")
            continue

    if not response:
        return "⚠️ Service temporarily experiencing high API load. Please resubmit your command in a few moments."

    if response.function_calls:
        for call in response.function_calls:
            if call.name == "create_reminder_tool":
                args = call.args
                
                with st.status("⚡ Reminder Agent: Processing Tool Execution...", expanded=True) as status_box:
                    st.write(f"**Function:** `create_reminder_tool`")
                    st.write(f"**Task Description:** `{args['task']}`")
                    st.write(f"**Calculated Time:** `{args['scheduled_time']}`")
                    
                    tool_result = create_reminder_tool(args['task'], args['scheduled_time'])
                    status_box.update(label="✅ Reminder successfully scheduled!", state="complete")

                tool_response_part = types.Part.from_function_response(
                    name=call.name,
                    response={"result": tool_result}
                )

                model_turn = response.candidates[0].content

                updated_contents = chat_contents + [
                    model_turn,
                    types.Content(role="user", parts=[tool_response_part])
                ]

                final_response = None
                for model_name in models_to_try:
                    try:
                        final_response = client.models.generate_content(
                            model=model_name,
                            contents=updated_contents,
                            config=types.GenerateContentConfig(system_instruction=system_instruction)
                        )
                        break
                    except Exception:
                        continue

                return final_response.text if final_response else "Scheduled successfully."

    return response.text

# -------------------------------------------------------------------
# 5. Main View: Workspace Chat
# -------------------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div class="hero-title">⏰ Reminder Agent</div>
    <div class="hero-subtitle">Autonomous Scheduling Workspace • Real-Time Tool Execution</div>
</div>
""", unsafe_allow_html=True)

# Live Status Indicator
st.markdown("""
<div class="agent-status-bar">
    <span class="status-pulse"></span>
    <span style="font-size: 0.85rem; font-weight: 600; color: #334155;">Agent Status: Online & Listening</span>
</div>
""", unsafe_allow_html=True)

# Render Chat Thread
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Input
if user_input := st.chat_input("Command your Reminder Agent (e.g., 'Remind me to submit team report in 10 minutes')"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing intent & calculating schedule parameters..."):
            try:
                agent_reply = run_agent_turn()
            except Exception as err:
                agent_reply = f"⚠️ Request failed: {err}. Please verify your API key and try again."

            st.markdown(agent_reply)
            st.session_state.messages.append({"role": "assistant", "content": agent_reply})

# -------------------------------------------------------------------
# 6. Sidebar: Control Panel & Dynamic Schedule Dashboard
# -------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Control Panel")
    
    # Real-Time System Clock Fragment (Ticks every 1 sec)
    @st.fragment(run_every=1)
    def render_live_clock():
        st.metric(
            label="System Date & Time", 
            value=datetime.now().strftime("%I:%M:%S %p"),
            delta=datetime.now().strftime("%Y-%m-%d")
        )
    
    render_live_clock()
    st.divider()

    # Active Schedule Dashboard Fragment (Ticks every 1 sec for smooth countdowns)
    @st.fragment(run_every=1)
    def render_scheduled_dashboard():
        st.subheader("📋 Active Reminders")
        
        if st.session_state.reminders:
            for idx, item in enumerate(st.session_state.reminders):
                now = datetime.now()
                time_left = int((item["target_dt"] - now).total_seconds())

                if item["status"] == "Active" and time_left <= 0:
                    item["status"] = "Triggered"
                    st.toast(f"**Reminder Alert:** {item['task']}", icon="⏰")

                with st.container(border=True):
                    cols = st.columns([2.5, 1.5])
                    with cols[0]:
                        st.markdown(f"**{item['task']}**")
                    with cols[1]:
                        badge_class = "status-badge-active" if item['status'] == "Active" else "status-badge-triggered"
                        st.markdown(f'<span class="{badge_class}">{item["status"]}</span>', unsafe_allow_html=True)
                    
                    # Live Countdown Calculation
                    if item['status'] == "Active" and time_left > 0:
                        mins, secs = divmod(time_left, 60)
                        hrs, mins = divmod(mins, 60)
                        countdown_str = f"⏳ In {hrs:02d}h {mins:02d}m {secs:02d}s"
                    else:
                        countdown_str = "⌛ Triggered"

                    st.caption(f"🕒 Due: `{item['scheduled_time']}`")
                    st.caption(f"**{countdown_str}**")
                    
                    # Action Buttons: Snooze & Cancel
                    if item['status'] == "Active":
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("➕ Snooze 5m", key=f"snooze_{item['id']}", use_container_width=True):
                                if item['id'] in st.session_state.timers:
                                    st.session_state.timers[item['id']].cancel()
                                
                                new_dt = item['target_dt'] + timedelta(minutes=5)
                                item['target_dt'] = new_dt
                                item['scheduled_time'] = new_dt.strftime("%Y-%m-%d %H:%M:%S")
                                
                                delay = (new_dt - datetime.now()).total_seconds()
                                new_timer = threading.Timer(delay, trigger_notification, args=[item['task']])
                                new_timer.start()
                                st.session_state.timers[item['id']] = new_timer
                                
                                st.toast(f"Snoozed '{item['task']}' for 5 minutes!", icon="⏰")
                                st.rerun()

                        with c2:
                            if st.button("Cancel", key=f"cancel_{item['id']}", type="secondary", use_container_width=True):
                                if item['id'] in st.session_state.timers:
                                    st.session_state.timers[item['id']].cancel()
                                    del st.session_state.timers[item['id']]
                                st.session_state.reminders.pop(idx)
                                st.rerun()
                            
            if st.button("Clear Dashboard", use_container_width=True, type="primary"):
                for timer in st.session_state.timers.values():
                    timer.cancel()
                st.session_state.timers.clear()
                st.session_state.reminders.clear()
                st.rerun()
        else:
            st.info("No active reminders currently queued.")

    render_scheduled_dashboard()