import os
from caspian import Caspian

# Initialize Caspian
caspian_client = Caspian(api_key=os.getenv("CASPIAN_API_KEY"))

def extract_procurement_details(user_text):
    """Uses Caspian to turn Slack text into structured data."""
    prompt = f"Identify the product and quantity from this request: '{user_text}'. Return as JSON."
    return caspian_client.generate(prompt=prompt)

def generate_comparison_blocks(vendor_quotes):
    """Formats a list of quotes into Slack Block Kit format."""
    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": "Vendor Quote Comparison"}},
        {"type": "divider"}
    ]
    
    for quote in vendor_quotes:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Vendor:* {quote['name']}\n*Price:* {quote['price']}\n*ETA:* {quote['eta']}"
            },
            "accessory": {
                "type": "button",
                "text": {"type": "plain_text", "text": "Select"},
                "value": quote['name'],
                "action_id": "select_vendor"
            }
        })
    return blocks
