from google.genai import Client, types
import os
from dotenv import load_dotenv
import json
import time

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

def draft_vendor_email(vendor_name, item, quantity, manager_instruction):
    prompt = f"""
    Write a B2B inquiry email to {vendor_name} for {quantity} {item}.
    Manager Instruction: {manager_instruction}
    
    Return the response in JSON format with two keys:
    "subject": A professional subject line
    "body": The email body text
    """

    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json" # This is the magic line
            )
        )
        return json.loads(response.text) # Returns a Python Dictionary
    except Exception as e:
        return {"subject": "Error", "body": str(e)}

def draft_outreach_emails(item, quantity, manager_note, vendor_list):
    """
    vendor_list: list of (name, email) tuples from the DB
    """
    all_drafts = []
    
    for name, email in vendor_list:
        prompt = f"""
        You are an AI Procurement Bot. 
        Write a professional B2B inquiry email to {name} ({email}).
        
        Task: Request a quote for {quantity} units of {item}.
        Manager Note: {manager_note}
        
        Return ONLY a JSON object with these keys:
        "recipient_email": The string '{email}'
        "vendor_name": The string '{name}'
        "subject": A professional subject line
        "body": The full email body text
        """
        
        try:
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            # Parse the JSON string into a dictionary
            email_dict = json.loads(response.text)
            all_drafts.append(email_dict)
            
        except Exception as e:
            print(f"Failed to draft for {name}: {e}")
        time.sleep(2)
            
    return all_drafts

if __name__ == "__main__":
    # Test 1: Simple Text
    print("Testing AI Text Parsing...")
    res = analyze_quote(email_text="Quote from Dell for 5 Monitors at 12000 each. contact: sales@dell.com")
    print(res)

    # Test 2: Intent Extraction (For the Manager's chat)
    print("\nTesting Intent Extraction...")
    intent = extract_search_intent("Show me the status for projectors")
    print(intent)

    print("\n--- Testing Email Writer ---")
    vendor = "Dell"
    item_name = "Monitors"
    price = 12000
    instruction = f"Ask if they can give a 10% discount for a bulk order of 20 units."

    email_draft = draft_vendor_email(vendor, item_name, price, instruction)
    print(email_draft)

        # --- TEST 1: Intent Extraction ---
    # This checks if the AI understands what the manager wants
    print("--- Testing Intent Extraction ---")
    manager_query = "Find me quotes for projectors and email the vendors for 10 units"
    intent = extract_search_intent(manager_query)
    print(f"Manager Intent: {intent}")

    # --- TEST 2: Multi-Email JSON Writer ---
    # We will provide a hardcoded list to simulate what the DB would return
    # This checks if your function loops through vendors and returns clean JSON
    print("\n--- Testing Multi-Email Writer ---")
    
    # Simulated vendor list (this is what your fetchall() usually looks like)
    mock_vendors = [
        ("Dell India", "sales@dell.in"),
        ("HP Global", "b2b@hp.com")
    ]
    
    # Call the function you just wrote
    drafts = draft_outreach_emails(
        item=intent['search_term'], 
        quantity="10", 
        manager_note="Budget is tight, need a discount.", 
        vendor_list=mock_vendors
    )

    # Print the results to verify the JSON structure
    for d in drafts:
        print(f"\nDraft for {d['vendor_name']}:")
        print(json.dumps(d, indent=2))