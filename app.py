import streamlit as st
import threading
from datetime import datetime
from plyer import notification
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Setup
st.set_page_config(
    page_title="TaskMind AI — Intelligent Reminder Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------
# 1. Professional Custom Styling (Light Theme)
# -------------------------------------------------------------------
st.markdown("""
<style>
    /* Header Styling */
    .agent-header {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        background: linear-gradient(90deg, #4F46E5, #06B6D4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        margin-bottom: 0px;
    }
    
    /* Sidebar Card Styles */
    .status-badge-active {
        background-color: #d1fae5;
        color: #047857;
        font-size: 0.75rem;
        padding: 3px 10px;
        border-radius: 12px;
        font-weight: 600;
    }

    .status-badge-triggered {
        background-color: #e0e7ff;
        color: #4338ca;
        font-size: 0.75rem;
        padding: 3px 10px;
        border-radius: 12px;
        font-weight: 600;
    }

    /* Primary Accent Button Styling */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #4F46E5, #6366F1);
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# 2. State Management & In-Memory Timer Registry
# -------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to **TaskMind AI**. I am your autonomous scheduling assistant.\n\nHow can I help organize your schedule today?"}
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
# 3. Thread-Safe Agent Tooling & System Alert Handler
# -------------------------------------------------------------------
def trigger_notification(task_name: str):
    """Fires native OS desktop notification."""
    try:
        notification.notify(
            title="⏰ TaskMind Alert",
            message=task_name,
            app_name="TaskMind AI",
            timeout=10
        )
    except Exception as e:
        print(f"Alert error: {e}")

def create_reminder_tool(task: str, scheduled_time: str) -> str:
    """Schedules a new reminder with active thread references."""
    try:
        target_dt = datetime.strptime(scheduled_time, "%Y-%m-%d %H:%M:%S")
        delay = (target_dt - datetime.now()).total_seconds()
        task_id = f"task_{int(datetime.now().timestamp())}"

        if delay > 0:
            # Pass ONLY string variables to background thread (NO st.session_state access)
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
            "target_dt": target_dt,  # Evaluated on main thread for status updates
            "status": status,
            "created_at": datetime.now().strftime("%H:%M:%S")
        })
        return f"SUCCESS: Scheduled '{task}' for {scheduled_time}."
    except Exception as e:
        return f"ERROR: Failed to parse execution time - {str(e)}"

# Function Tool Definition
reminder_tool_decl = types.FunctionDeclaration(
    name="create_reminder_tool",
    description="Schedules a task to run at an absolute timestamp (YYYY-MM-DD HH:MM:SS format).",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "task": types.Schema(type=types.Type.STRING, description="Description of the task."),
            "scheduled_time": types.Schema(type=types.Type.STRING, description="Target datetime string (YYYY-MM-DD HH:MM:SS)."),
        },
        required=["task", "scheduled_time"],
    ),
)

tools_config = types.Tool(function_declarations=[reminder_tool_decl])

# -------------------------------------------------------------------
# 4. Core Agent Reasoning Engine
# -------------------------------------------------------------------
def run_agent_turn():
    client = genai.Client()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    system_instruction = (
        f"You are TaskMind AI, an enterprise-grade autonomous scheduling assistant. Current time: {now_str}.\n\n"
        "CORE RESPONSIBILITIES:\n"
        "1. Schedule tasks precision-calculated relative to current time.\n"
        "2. PARAMETER GATHERING: If the prompt lacks exact details (e.g., missing date/time or task context), "
        "do not attempt tool execution. Respectfully request missing fields.\n"
        "3. DOMAIN BOUNDARIES: Reject off-topic general knowledge/trivia requests politely. Focus strictly on task management.\n"
        "4. Call `create_reminder_tool` immediately when parameters are completely resolved."
    )

    chat_contents = get_gemini_chat_history()

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=chat_contents,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[tools_config],
            temperature=0.1
        )
    )

    if response.function_calls:
        for call in response.function_calls:
            if call.name == "create_reminder_tool":
                args = call.args
                
                with st.status("⚡ Agent Execution: Dispatching Tool...", expanded=True) as status_box:
                    st.write(f"**Function:** `create_reminder_tool`")
                    st.write(f"**Parsed Task:** `{args['task']}`")
                    st.write(f"**Calculated Time:** `{args['scheduled_time']}`")
                    
                    tool_result = create_reminder_tool(args['task'], args['scheduled_time'])
                    status_box.update(label="✅ Task successfully committed to system thread schedule!", state="complete")

                tool_response_part = types.Part.from_function_response(
                    name=call.name,
                    response={"result": tool_result}
                )

                model_turn = response.candidates[0].content

                updated_contents = chat_contents + [
                    model_turn,
                    types.Content(role="user", parts=[tool_response_part])
                ]

                final_response = client.models.generate_content(
                    model="gemini-3.1-flash-lite",
                    contents=updated_contents,
                    config=types.GenerateContentConfig(system_instruction=system_instruction)
                )

                return final_response.text

    return response.text

# -------------------------------------------------------------------
# 5. Main UI Layout & Live Components
# -------------------------------------------------------------------
st.markdown('<p class="agent-header">🤖 TaskMind AI</p>', unsafe_allow_html=True)
st.caption("Autonomous Agent Workspace • Real-Time Tool Execution & System Threading")
st.divider()

# Stream Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Input
if user_prompt := st.chat_input("Command your agent (e.g., 'Remind me to join team sync in 5 minutes')"):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processing intent & calculating parameters..."):
            agent_reply = run_agent_turn()
            st.markdown(agent_reply)
            st.session_state.messages.append({"role": "assistant", "content": agent_reply})

# -------------------------------------------------------------------
# 6. Professional Auto-Refreshing Dashboard Sidebar
# -------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Task Dashboard")
    
    # Live System Clock Fragment (Ticks every 1 sec)
    @st.fragment(run_every=1)
    def render_live_clock():
        st.metric(
            label="System Date & Time", 
            value=datetime.now().strftime("%I:%M:%S %p"),
            delta=datetime.now().strftime("%Y-%m-%d")
        )
    
    render_live_clock()
    st.divider()

# Real-Time Task Schedule Fragment (Ticks every 3 seconds)
    @st.fragment(run_every=3)
    def render_scheduled_dashboard():
        st.subheader("📋 Active Schedule")
        
        if st.session_state.reminders:
            for idx, item in enumerate(st.session_state.reminders):
                # Check if an active reminder has hit its due time
                if item["status"] == "Active" and datetime.now() >= item.get("target_dt", datetime.now()):
                    item["status"] = "Triggered"
                    
                    # 🔔 IN-APP BROWSER NOTIFICATION
                    st.toast(f"**Reminder Alert:** {item['task']}", icon="⏰")

                with st.container(border=True):
                    cols = st.columns([3, 1])
                    with cols[0]:
                        st.markdown(f"**{item['task']}**")
                    with cols[1]:
                        badge_class = "status-badge-active" if item['status'] == "Active" else "status-badge-triggered"
                        st.markdown(f'<span class="{badge_class}">{item["status"]}</span>', unsafe_allow_html=True)
                    
                    st.caption(f"🕒 Due: `{item['scheduled_time']}`")
                    
                    # Action: Allow manual cancellation of active thread timers
                    if item['status'] == "Active":
                        if st.button("Cancel Task", key=f"cancel_{item['id']}", type="secondary", use_container_width=True):
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
            st.info("No tasks currently queued.")

    render_scheduled_dashboard()