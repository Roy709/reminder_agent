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
# 1. Cross-Browser CSS Styling System (Localized Sidebar Scrollbar)
# -------------------------------------------------------------------
st.markdown("""
<style>
    /* Global Page Body Reset */
    .stApp {
        background-color: #ffffff !important;
        color: #0f172a !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Permanently Hide Sidebar Collapse/Expand Toggle Controls (<< and >>) */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* Force Sidebar Open & Fixed Width */
    [data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 1px solid #e2e8f0;
        min-width: 360px !important;
        max-width: 360px !important;
    }

    /* Disable Outer Sidebar Container Scrollbar */
    [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        padding-top: 0rem !important;
        overflow-y: hidden !important;
        overflow-x: hidden !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
        display: none !important;
        height: 0px !important;
        min-height: 0px !important;
        padding: 0px !important;
        margin: 0px !important;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
        padding-top: 0.5rem !important;
        margin-top: 0.5rem !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
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

    /* Remove Invisible Top Header Padding */
    [data-testid="stHeader"] {
        display: none !important;
    }

    /* Main Screen Container Spacing Optimization */
    .stMainBlockContainer,
    [data-testid="stMainBlockContainer"],
    .main .block-container {
        padding-top: 0.5rem !important;
        margin-top: 0rem !important;
        padding-bottom: 0.5rem !important;
        max-width: 850px;
    }

    /* Modern Centered Greeting Header */
    .welcome-header {
        text-align: center;
        margin-top: 0.5rem;
        margin-bottom: 0.75rem;
    }
    .welcome-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0f172a !important;
        margin-bottom: 4px;
    }
    .welcome-subtitle {
        font-size: 0.95rem;
        color: #64748b !important;
    }

    /* Force Light Theme Colors on Chat Messages Across All Browsers */
    [data-testid="stChatMessage"], 
    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] span,
    .stChatMessage [data-testid="stMarkdownContainer"] p {
        color: #0f172a !important;
        font-weight: 500 !important;
    }

    /* Hide Deploy Button & Main Menu */
    .stAppDeployButton, #MainMenu {
        display: none !important;
    }

    /* Floating Chat Input Box Gap Optimization */
    [data-testid="stBottom"] {
        padding-bottom: 0.5rem !important;
        padding-top: 0rem !important;
    }
    
    [data-testid="stBottom"] > div {
        padding-top: 0rem !important;
        background-color: #ffffff !important;
    }

    [data-testid="stChatInput"], 
    [data-testid="stChatInput"] > div, 
    [data-baseweb="base-input"], 
    [data-baseweb="input"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03) !important;
    }
    [data-testid="stChatInput"] * {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #64748b !important;
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
        justify-content: center;
        gap: 8px;
        margin-bottom: 1rem;
        background-color: #ffffff;
        padding: 6px 14px;
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        width: fit-content;
        margin-left: auto;
        margin-right: auto;
    }
    .status-pulse {
        height: 8px;
        width: 8px;
        background-color: #22c55e;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
        animation: pulse-green 2s infinite;
    }
    @keyframes pulse-green {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(34, 197, 94, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
    }

    /* Chat Messages Container Inner Border Removal */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: none !important;
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

if "preset_input" not in st.session_state:
    st.session_state.preset_input = None

def get_gemini_chat_history():
    history = []
    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "model"
        history.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))
    return history

# -------------------------------------------------------------------
# 3. Notification & Tool Execution Logic
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

def update_reminder_tool(search_query: str, new_scheduled_time: str, new_task_name: str = None) -> str:
    """Modifies an existing reminder instead of creating a duplicate entry."""
    target_item = None
    for item in st.session_state.reminders:
        if search_query.lower() in item["task"].lower():
            target_item = item
            break

    if not target_item:
        return f"ERROR: Could not find an active reminder matching query '{search_query}'."
    
    if target_item["status"] == "Triggered":
        return f"NOTICE: The reminder '{target_item['task']}' has already been triggered and completed. Please create a new reminder instead."

    try:
        new_target_dt = datetime.strptime(new_scheduled_time, "%Y-%m-%d %H:%M:%S")
        
        # Cancel old timer thread
        if target_item['id'] in st.session_state.timers:
            st.session_state.timers[target_item['id']].cancel()

        # Update reminder fields
        if new_task_name:
            target_item["task"] = new_task_name
        target_item["scheduled_time"] = new_scheduled_time
        target_item["target_dt"] = new_target_dt

        # Re-arm timer thread
        delay = (new_target_dt - datetime.now()).total_seconds()
        if delay > 0:
            timer = threading.Timer(delay, trigger_notification, args=[target_item["task"]])
            timer.start()
            st.session_state.timers[target_item['id']] = timer
            target_item["status"] = "Active"
        else:
            trigger_notification(target_item["task"])
            target_item["status"] = "Triggered"

        return f"SUCCESS: Updated reminder '{target_item['task']}' to run at {new_scheduled_time}."
    except Exception as e:
        return f"ERROR: Failed to update reminder - {str(e)}"

# Function Tool Declarations
reminder_tool_decl = types.FunctionDeclaration(
    name="create_reminder_tool",
    description="Schedules a NEW reminder task at an absolute timestamp (YYYY-MM-DD HH:MM:SS format).",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "task": types.Schema(type=types.Type.STRING, description="Description of the task or reminder."),
            "scheduled_time": types.Schema(type=types.Type.STRING, description="Target datetime string (YYYY-MM-DD HH:MM:SS)."),
        },
        required=["task", "scheduled_time"],
    ),
)

update_tool_decl = types.FunctionDeclaration(
    name="update_reminder_tool",
    description="Updates or postpones an EXISTING active reminder matching a search query.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "search_query": types.Schema(type=types.Type.STRING, description="Task name or keyword to locate the existing reminder."),
            "new_scheduled_time": types.Schema(type=types.Type.STRING, description="New target datetime string (YYYY-MM-DD HH:MM:SS)."),
            "new_task_name": types.Schema(type=types.Type.STRING, description="Optional updated task description text."),
        },
        required=["search_query", "new_scheduled_time"],
    ),
)

tools_config = types.Tool(function_declarations=[reminder_tool_decl, update_tool_decl])

# -------------------------------------------------------------------
# 4. Core Agent Reasoning Engine
# -------------------------------------------------------------------
def run_agent_turn():
    client = genai.Client()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Construct active reminders list so agent can resolve updates accurately
    active_reminders_summary = "\n".join([f"- {r['task']} (Due: {r['scheduled_time']})" for r in st.session_state.reminders if r['status'] == 'Active'])

    system_instruction = (
        f"You are the Reminder Agent, an autonomous scheduling assistant. Current system timestamp: {now_str}.\n\n"
        f"CURRENT ACTIVE REMINDERS:\n{active_reminders_summary if active_reminders_summary else 'No active reminders.'}\n\n"
        "CORE RESPONSIBILITIES:\n"
        "1. Schedule NEW tasks precision-calculated relative to system timestamp using `create_reminder_tool`.\n"
        "2. UPDATE/POSTPONE EXISTING tasks using `update_reminder_tool` whenever user asks to change, move, postpone, or update a task. "
        "Match the `search_query` parameter to the exact task name from the CURRENT ACTIVE REMINDERS list above.\n"
        "3. PARAMETER GATHERING: If the prompt lacks exact details, respectfully request missing fields.\n"
        "4. Call the appropriate tool function immediately when parameters are resolved."
    )

    chat_contents = get_gemini_chat_history()

    models_to_try = [
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.1-flash-lite"
    ]
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
            if call.name in ["create_reminder_tool", "update_reminder_tool"]:
                args = call.args
                
                with st.status(f"⚡ Processing Tool: `{call.name}`...", expanded=True) as status_box:
                    if call.name == "create_reminder_tool":
                        st.write(f"**Task Description:** `{args['task']}`")
                        st.write(f"**Calculated Time:** `{args['scheduled_time']}`")
                        tool_result = create_reminder_tool(args['task'], args['scheduled_time'])
                    else:
                        st.write(f"**Target Task:** `{args['search_query']}`")
                        st.write(f"**New Time:** `{args['new_scheduled_time']}`")
                        tool_result = update_reminder_tool(
                            search_query=args['search_query'],
                            new_scheduled_time=args['new_scheduled_time'],
                            new_task_name=args.get('new_task_name')
                        )
                    
                    status_box.update(label="✅ Operation execution complete!", state="complete")

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

                return final_response.text if final_response else "Operation processed successfully."

    return response.text

# -------------------------------------------------------------------
# 5. Main View: Centered Modern Workspace
# -------------------------------------------------------------------
st.markdown("""
<div class="welcome-header">
    <div class="welcome-title">What can I schedule for you today?</div>
    <div class="welcome-subtitle">Specify any task using natural, relative time commands</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="agent-status-bar">
    <span class="status-pulse"></span>
    <span style="font-size: 0.8rem; font-weight: 600; color: #475569;">Agent Status: Online & Listening</span>
</div>
""", unsafe_allow_html=True)

chat_container = st.container(height=520, border=False)

with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

user_prompt = st.chat_input("Command your Reminder Agent (e.g., 'Update client meeting reminder to 2 hours')")
active_input = st.session_state.preset_input or user_prompt

if active_input:
    st.session_state.preset_input = None
    st.session_state.messages.append({"role": "user", "content": active_input})
    with chat_container:
        with st.chat_message("user"):
            st.markdown(active_input)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing intent & calculating schedule parameters..."):
                try:
                    agent_reply = run_agent_turn()
                except Exception as err:
                    agent_reply = f"⚠️ Request failed: {err}. Please verify your API key and try again."

                st.markdown(agent_reply)
                st.session_state.messages.append({"role": "assistant", "content": agent_reply})
                st.rerun()

# -------------------------------------------------------------------
# 6. Sidebar: Fixed Header + Isolated Scroll Container for Reminders
# -------------------------------------------------------------------
with st.sidebar:
    st.title("⏰ Reminder Agent")
    
    @st.fragment(run_every=1)
    def render_live_clock():
        st.metric(
            label="System Date & Time", 
            value=datetime.now().strftime("%I:%M:%S %p"),
            delta=datetime.now().strftime("%Y-%m-%d")
        )
    
    render_live_clock()
    st.divider()

    @st.fragment(run_every=1)
    def render_scheduled_dashboard():
        st.subheader("📋 Active Reminders")
        
        if st.session_state.reminders:
            # Isolated Scroll Container for Reminder Cards Only (Fixed Height 420px)
            reminder_scroll_box = st.container(height=420, border=False)
            
            with reminder_scroll_box:
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
                        
                        if item['status'] == "Active" and time_left > 0:
                            mins, secs = divmod(time_left, 60)
                            hrs, mins = divmod(mins, 60)
                            countdown_str = f"⏳ In {hrs:02d}h {mins:02d}m {secs:02d}s"
                        else:
                            countdown_str = "⌛ Triggered"

                        st.caption(f"🕒 Due: `{item['scheduled_time']}`")
                        st.caption(f"**{countdown_str}**")
                        
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