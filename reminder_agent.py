from google import genai
from google.genai import types
from datetime import datetime
from pydantic import BaseModel
import time
import threading
import schedule
from plyer import notification

# -------------------------------------------------------------------
# 1. Define Output Schema for Gemini Tool Call / Structured Output
# -------------------------------------------------------------------
class ReminderSchema(BaseModel):
    task: str
    scheduled_time: str  # Format: YYYY-MM-DD HH:MM:SS

# -------------------------------------------------------------------
# 2. AI Parsing Layer using Gemini
# -------------------------------------------------------------------
def parse_reminder_with_gemini(user_prompt: str) -> ReminderSchema:
    client = genai.Client()
    current_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    system_instruction = (
        f"You are a scheduling AI assistant. The current date and time is {current_now}. "
        "Extract the task name and exact execution target date/time from the user's prompt. "
        "Convert relative times (e.g., 'in 10 minutes', 'tomorrow at 3pm') into absolute timestamp "
        "formatted strictly as YYYY-MM-DD HH:MM:SS."
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=ReminderSchema,
            temperature=0.1
        )
    )

    return ReminderSchema.model_validate_json(response.text)

# -------------------------------------------------------------------
# 3. Execution & Notification Layer
# -------------------------------------------------------------------
def trigger_notification(task_name: str):
    print(f"\n[ALERT TRIGGERED] Reminder: {task_name}")
    
    # Desktop Popup Notification
    try:
        notification.notify(
            title="AI Reminder Agent",
            message=task_name,
            app_name="Reminder Agent",
            timeout=10
        )
    except Exception as e:
        print(f"Desktop notification failed: {e}")

def schedule_reminder(task: str, run_at: datetime):
    delay_seconds = (run_at - datetime.now()).total_seconds()
    
    if delay_seconds <= 0:
        print("The scheduled time is in the past! Triggering immediately...")
        trigger_notification(task)
        return

    # Use a threading Timer for precise execution
    timer = threading.Timer(delay_seconds, trigger_notification, args=[task])
    timer.start()
    print(f"Scheduled: '{task}' for {run_at.strftime('%Y-%m-%d %H:%M:%S')} ({int(delay_seconds)}s from now)")

# -------------------------------------------------------------------
# 4. Main Agent Loop
# -------------------------------------------------------------------
def run_agent():
    print("=== Gemini Reminder Agent Active ===")
    print("Type 'exit' to quit.\n")
    
    while True:
        user_input = input("Enter a reminder prompt > ")
        if user_input.lower() in ["exit", "quit"]:
            break

        try:
            # Step A: Parse input using Gemini
            parsed = parse_reminder_with_gemini(user_input)
            target_dt = datetime.strptime(parsed.scheduled_time, "%Y-%m-%d %H:%M:%S")

            # Step B: Register into system scheduler
            schedule_reminder(parsed.task, target_dt)

        except Exception as e:
            print(f"Error processing prompt: {e}\n")

if __name__ == "__main__":
    run_agent()