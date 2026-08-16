import os
import time
from dotenv import load_dotenv
from caspian_sdk import CommClient
import main  

load_dotenv()

# Initialize Caspian Client
client = CommClient(api_key=os.getenv("CASPIAN_API_KEY"))

@client.on_message
def handle_incoming(message):
    """Passes every incoming message to the main controller."""
    try:
        main.coordinate_flow(message, client)
    except Exception as e:
        print(f"Controller Error: {e}")

if __name__ == "__main__":
    print("AI Procurement Bot is starting...")
    
    # 1. Connect to Slack
    client.connect_slack(
        bot_token=os.getenv("SLACK_BOT_TOKEN"),
        app_token=os.getenv("SLACK_APP_TOKEN")
    )
    
    # 2. Connect Email and update global ID
    try:
        conn = client.connect_email(username="procure-bot")
        main.EMAIL_CONN_ID = conn.get("id") if isinstance(conn, dict) else conn
        print(f"Email Connected: {main.EMAIL_CONN_ID}")
    except Exception as e:
        print(f"Email Connection Failed: {e}")

    # 3. Start Listening for new Slack/Email events
    while True:
        try:
            client.listen()
        except Exception as e:
            print(f"Connection dropped: {e}. Reconnecting...")
            time.sleep(5)