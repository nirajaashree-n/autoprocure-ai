import os
from dotenv import load_dotenv
from caspian_sdk import CommClient

load_dotenv()

# Initialize Caspian Client
client = CommClient(api_key=os.getenv("CASPIAN_API_KEY"))

# 1. Connect Slack (The "Pocket" Interface)
client.connect_slack(
    bot_token=os.getenv("SLACK_BOT_TOKEN"),
    app_token=os.getenv("SLACK_APP_TOKEN")
)

# 2. Connect Email (The Vendor Interface)
# This generates a unique agent email address automatically
inbox = client.connect_email()
print(f"--- PROCUREMENT AGENT ACTIVE ---")
print(f"Agent Email: {inbox['address']}")
print(f"--------------------------------")

# Pre-approved vendor list (Demo purposes)
VENDORS = ["vendor-a@example.com", "vendor-b@example.com"]

# 3. THE SINGLE HANDLER (Hackathon Requirement)
@client.on_message
def handle_procurement(message):
    # --- CHANNEL 1: SLACK (From Business Owner) ---
    if message.provider == "slack":
        query = message.text
        message.reply(f"I'm requesting quotes for: *{query}*")
        
        # Send emails to all vendors
        for vendor in VENDORS:
            client.send_email(
                to=vendor,
                subject=f"Quote Request: {query}",
                body=f"Hi, we need a quote for {query}. Please reply with your best price."
            )

    # --- CHANNEL 2: EMAIL (From Vendors) ---
    elif message.provider == "email":
        vendor_email = message.sender.get("address")
        quote_text = message.text
        
        # Send a summary table back to the Owner on Slack
        client.send_slack(
            channel="general", # Or your specific channel name
            text=(
                f"*New Quote Received!*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"*Vendor:* {vendor_email}\n"
                f"*Details:* {quote_text}\n"
                f"━━━━━━━━━━━━━━━━━━━━"
            )
        )

# 4. Run the Agent
client.listen()

