import os
import time
import re
from dotenv import load_dotenv
from caspian_sdk import CommClient

load_dotenv()

client = CommClient(api_key=os.getenv("CASPIAN_API_KEY"))

email_conn_id = None
slack_conversation_id = None 

def get_email_connection():
    try:
        conn = client.connect_email(username="procure-bot")
        conn_id = conn.get("id") if isinstance(conn, dict) else conn
        print(f"Email Connection Active: {conn_id}")
        return conn_id
    except Exception as e:
        print(f"Connection Error: {e}")
        return None

email_conn_id = get_email_connection()

# This is where we define how the bot should behave when replying
client.behavior_prompt = (
    "You are a professional procurement assistant. When acknowledging a request, "
    "be brief and professional. When summarizing a quote, use a clean list or table format."
)

VENDORS = ["nityashreeneelakandan@gmail.com"]

@client.on_message
def handle_procurement(message):
    global email_conn_id, slack_conversation_id
    
    is_email = getattr(message, 'subject', None) is not None

    if not is_email:
        # --- 1. HANDLING SLACK REQUESTS ---
        slack_conversation_id = message.conversation_id
        text = message.text
        
        # Logic to extract quantity and item using Regex
        # Matches a number followed by words (e.g., "20 desks" or "5 laptops")
        match = re.search(r'(\d+)\s+(.*)', text)
        
        if match:
            qty = match.group(1)   # The number (e.g., 20)
            item = match.group(2)  # Everything after the number (e.g., desks)
        else:
            qty = "a certain amount of"
            item = text # Fallback to the whole message if no number is found
            
        # Proper Reply to Slack
        message.reply(f"I'm on it! Sourcing quotes for *{qty} {item}*.")
        
        for vendor in VENDORS:
            try:
                client.initiate(
                    connection_id=email_conn_id,
                    recipient=vendor,
                    text=f"Request for Quote: {qty} {item}. Please reply with your best price."
                )
                print(f"RFQ sent to {vendor}")
            except Exception as e:
                print(f"Email Error: {e}")


                
    else:
        # --- 2. HANDLING VENDOR REPLIES ---
        sender_email = message.sender.get('address') if isinstance(message.sender, dict) else str(message.sender)
        
        # Clean the email history
        raw_text = message.text
        # Split at common "On [Date], [Name] wrote:" markers
        clean_text = raw_text.split("On Tue,")[0].split("On Wed,")[0].split("On Mon,")[0].split("-----Original Message-----")[0].strip()
        
        print(f"Vendor Reply Received from {sender_email}")

        try:
            if slack_conversation_id:
                # We send the cleaned text back to Slack. 
                # The behavior_prompt will help the user see this as a 'Quote Summary'.
                client.send_message(
                    conversation_id=slack_conversation_id,
                    text=f"*New Quote from {sender_email}*:\n\n{clean_text}"
                )
                print("Summary sent to Slack.")
        except Exception as e:
            print(f"Forwarding Error: {e}")

if __name__ == "__main__":
    client.connect_slack(
        bot_token=os.getenv("SLACK_BOT_TOKEN"),
        app_token=os.getenv("SLACK_APP_TOKEN")
    )
        
    while True:
        try:
            client.listen()
        except Exception as e:
            time.sleep(5)
