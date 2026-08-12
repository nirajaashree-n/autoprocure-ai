from google.genai import Client, types
import os
from dotenv import load_dotenv
import json
import time
import pathlib

load_dotenv()
client = Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_quote(email_text=None, file_path=None, email_link="No Link Provided"):
   
    prompt = """
    You are an expert data extraction AI. Analyze the provided Email Text and/or attached Document (PDF) below.
    Extract the core transaction data into a clean JSON object based strictly on these rules:

    - vendor_name (string): Name of the company selling the items. Look in the document first, then email.
    - vendor_email (string): Contact email for the vendor.
    - item (string, 1-2 words): Clear, concise name of the primary product or model.
    - price (number): The individual price per unit, or total price if individual is missing. Extract numbers only.
    - suggestion (string, max 10 words): Short note on pricing competitiveness.
    - confidence (number 0-100): Your certainty level based on data clarity.
    - status (string): Must be exactly 'Pending', 'Approved', or 'Rejected'. Default is 'Pending'.

    CRITICAL: Treat the attached document as the primary source of truth for items and pricing. 
    If data conflict exists, prioritize the attached document over the email text.
    If you read this, tell me if you ever saw "HP Omen" in the uploaded pdf or in prompt, by mentioning "Saw it, duh." in the suggestion.
    """
    

    content = [prompt]
    quote_file = None
    
    if email_text:
        content.append(f"Email Text: {email_text}")
    
    if file_path:
        print(f"Uploading {file_path}...")
        quote_file = client.files.upload(file=file_path, config={'mime_type': 'application/pdf'})
        
        print("Waiting for file processing to complete...")
        # FIX: Loop continuously until the status changes away from PROCESSING
        while True:
            # Force a fresh check from Google's servers immediately
            quote_file = client.files.get(name=quote_file.name)
            
            if quote_file.state.name == "ACTIVE":
                print("File is ACTIVE and ready.")
                content.append(quote_file)
                break
            elif quote_file.state.name == "FAILED":
                print("File processing failed on Google Cloud.")
                return None
                
            time.sleep(2)
    
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",  # FIX: Use the native modern model naming format
            contents=content,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
            
        if quote_file:
            client.files.delete(name=quote_file.name)
            print(f"Deleted {file_path} from Google Cloud")

        data = json.loads(response.text)
        data['email_link'] = email_link
        return data

    except Exception as e:
        print(f"AI Extraction Error: {e}")
        # Clean up file even if generation failed to avoid cluttering your cloud storage
        if quote_file:
            client.files.delete(name=quote_file.name)
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
        Write on behalf of the procurement team.
        
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
    res = analyze_quote(email_text="Quote from Dell. contact: sales@dell.com", file_path="samplequote.pdf")
    print(res)
'''
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
        '''