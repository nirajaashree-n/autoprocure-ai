from google.genai import Client, types
import os
from dotenv import load_dotenv
import json
import time
import pathlib

load_dotenv()

def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    return Client(api_key=api_key)

def analyze_quote(email_text=None, file_path=None, email_link="No Link Provided"):
    client = get_client()
    prompt = """
    CRITICAL INSTRUCTION: Extract the TOTAL QUOTE AMOUNT.
    Look for keywords like 'Total', 'Grand Total', 'Net Amount', or 'Amount Payable'.
    
    Return a JSON object:
    - vendor_name: name of the company
    - price: Return ONLY the digits. (Example: If it is Rs. 7,50,000, return "7500000")
    - item: The product name
    - suggestion: If "HP Omen" is mentioned anywhere, return "Saw it, duh."
    - confidence: 0-100
    
    If you cannot find a price, look at the unit price and quantity and calculate it.
    """
    
    content = [prompt]
    quote_file = None 
    
    if email_text:
        content.append(f"Email Text: {email_text}")
    
    if file_path and os.path.exists(file_path):
        quote_file = client.files.upload(file=file_path, config={'mime_type': 'application/pdf'})
        while True:
            quote_file = client.files.get(name=quote_file.name)
            if quote_file.state.name == "ACTIVE":
                content.append(quote_file)
                break
            elif quote_file.state.name == "FAILED":
                return None
            time.sleep(2)
    
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash", 
            contents=content,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        if quote_file:
            client.files.delete(name=quote_file.name)
        data = json.loads(response.text)
        data['email_link'] = email_link
        return data
    except Exception as e:
        print(f"AI Extraction Error: {e}")
        return None

def extract_search_intent(manager_message):
    client = get_client()
    prompt = f"""
    Analyze: "{manager_message}"
    Extract the search term. Return JSON: {{"search_term": "string", "type": "item|id"}}
    """
    response = client.models.generate_content(
<<<<<<< HEAD
        model="gemini-3.6-flash",
=======
        model="gemini-3.5-flash",
>>>>>>> 0255006 (Updated code)
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(response.text)

def generate_slack_reply(manager_message, raw_data):
<<<<<<< HEAD
    client = get_client()
    prompt = f"Manager asked: '{manager_message}'. Data: {raw_data}. Summarize concise for Slack."
    response = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
=======
    
    #Turns DB rows into a nice Slack response + email draft suggestion.
    

    prompt = f"""
    Manager asked: "{manager_message}"
    Data found in DB: {raw_data}
    
    Task: 
    1. Summarize the status.
    Keep it concise for Slack.
    """
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )
>>>>>>> 0255006 (Updated code)
    return response.text

def draft_vendor_email(vendor_name, item, quantity, manager_instruction):
    client = get_client()
    prompt = f"Draft B2B email to {vendor_name} for {quantity} {item}. Note: {manager_instruction}. Return JSON: {{'subject': '...', 'body': '...'}}"
    try:
        response = client.models.generate_content(
<<<<<<< HEAD
            model="gemini-3.6-flash",
=======
            model="gemini-3.5-flash",
>>>>>>> 0255006 (Updated code)
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        return {"subject": "Error", "body": str(e)}

def draft_outreach_emails(item, quantity, manager_note, vendor_list):
    client = get_client()
    all_drafts = []
    for name, email in vendor_list:
        prompt = f"Draft outreach to {name} ({email}) for {quantity} {item}. Note: {manager_note}. Return JSON: {{'recipient_email': '{email}', 'vendor_name': '{name}', 'subject': '...', 'body': '...'}}"
        try:
            response = client.models.generate_content(
<<<<<<< HEAD
                model="gemini-3.6-flash",
=======
                model="gemini-3.5-flash",
>>>>>>> 0255006 (Updated code)
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            all_drafts.append(json.loads(response.text))
        except Exception as e:
            print(f"Failed for {name}: {e}")
        time.sleep(2)
    return all_drafts
if __name__ == "__main__":
    # Test block remains unchanged
    print("Testing AI Text Parsing...")
    res = analyze_quote(email_text="Quote from Dell. contact: sales@dell.com")
    print(res)
