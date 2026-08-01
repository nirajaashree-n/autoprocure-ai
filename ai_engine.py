from google.genai import Client, types
import os
from dotenv import load_dotenv
import json

load_dotenv()
client = Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_quote(email_text=None, file_path=None, email_link="No Link Provided"):
   
    prompt = """
    Extract data into JSON:
    - vendor_name (string)
    - vendor_email (string)
    - item (string, 1-2 words) (Clear, concise, short)
    - price (number)
    - suggestion (string, max 10 words) (Like, is this price competitive, too high compared to other quotes, absolute lowest, etc)
    - confidence (number 0-100) (depends on how sure you are of this response, based on clarity of data)
    - status (string, single word) (Three words only: Pending, Approved, Rejected; default is Pending)
    """

    content = [prompt]
    quote_file = None
    
    # Add text if available
    if email_text:
        content.append(f"Email Text: {email_text}")
    
    # Add PDF if available using Gemini's native File API
    if file_path:
        quote_file = client.files.upload(path=file_path)
        content.append(quote_file)

    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=content,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        if quote_file:
            client.files.delete(quote_file.name)
            print(f" Deleted {file_path} from Google Cloud")

        data = json.loads(response.text)
        data['email_link'] = email_link
        return data

    except Exception as e:
        print(f" AI Extraction Error: {e}")
        return None

def extract_search_intent(manager_message):
    
    #Interprets manager's Slack message to find the 'Item Name' or 'Quote ID'.
    
    
    prompt = f"""
    Analyze the manager's request: "{manager_message}"
    Extract the search term. 
    - If they mention a product, return the product name.
    - If they mention an ID number, return the ID.
    - Return JSON: {{"search_term": "string", "type": "item|id"}}
    """
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    return json.loads(response.text)

def generate_slack_reply(manager_message, raw_data):
    
    #Turns DB rows into a nice Slack response + email draft suggestion.
    

    prompt = f"""
    Manager asked: "{manager_message}"
    Data found in DB: {raw_data}
    
    Task: 
    1. Summarize the status.
    Keep it concise for Slack.
    """
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )
    return response.text

if __name__ == "__main__":
    # Test 1: Simple Text
    print("Testing AI Text Parsing...")
    res = analyze_quote(email_text="Quote from Dell for 5 Monitors at 12000 each. contact: sales@dell.com")
    print(res)

    # Test 2: Intent Extraction (For the Manager's chat)
    print("\nTesting Intent Extraction...")
    intent = extract_search_intent("Show me the status for projectors")
    print(intent)

