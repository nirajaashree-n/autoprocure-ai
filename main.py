import ai_engine      # The AI logic
import caspian_logic  # The UI logic
import db_manager     # The Database logic
import os
import time           # For rate-limit prevention

# Global state
EMAIL_CONN_ID = "conn_fc1c04a1ab7bc0fa9e28a802"
SLACK_CHAT_ID = None 
# This global variable ensures all vendors are grouped in one table
CURRENT_ITEM = "Requested Item" 

# Add your vendor emails to this list
VENDORS = ["nityashreeneelakandan@gmail.com", "nirajaashreeneelakandan@gmail.com"]

def coordinate_flow(message, client):
    """
    Main entry point for all messages. 
    Coordinates Slack requests and Email responses.
    """
    global SLACK_CHAT_ID, EMAIL_CONN_ID, CURRENT_ITEM
    
    # Check if the message is an Email (Vendor) or Slack (Owner)
    is_email = hasattr(message, 'subject') and message.subject is not None

    if not is_email:
        # --- PHASE 1: OWNER REQUEST (SLACK) ---
        SLACK_CHAT_ID = message.conversation_id
        
        # 1. AI: Understand what the owner wants
        intent = ai_engine.extract_search_intent(message.text)
        CURRENT_ITEM = intent.get("search_term", "items")
        
        message.reply(f"Analyzing your request for *{CURRENT_ITEM}*...")
        
        # 2. Check Database for existing data
        db_manager.init_db()
        past_quotes = db_manager.fetch_data_by_keyword(CURRENT_ITEM)
        
        # Check if past_quotes is not empty to avoid 'NoneType' errors
        if past_quotes and len(past_quotes) > 0:
            q = past_quotes[0] # Get latest match
            # Sending as text to avoid block validation issues
            client.send_message(
                conversation_id=SLACK_CHAT_ID, 
                text=f"Found past quote: {q[1]} - ${q[4]}"
            )

        # 3. AI: Draft and Send RFQs to Vendors
        for v_email in VENDORS:
            # Small cooldown to prevent Gemini 429 errors
            time.sleep(2) 
            
            draft = ai_engine.draft_vendor_email("Supplier", CURRENT_ITEM, "Multiple", message.text)
            client.initiate(
                connection_id=EMAIL_CONN_ID,
                recipient=v_email,
                text=f"Subject: {draft.get('subject')}\n\n{draft.get('body')}"
            )
        
        print(f"RFQs sent out for: {CURRENT_ITEM}")

    else:
        # --- PHASE 2: VENDOR REPLY (EMAIL) ---
        sender_email = message.sender.get('address') if isinstance(message.sender, dict) else str(message.sender)
            
        # 1. Initialize variables with defaults
        v_name = "Vendor"
        v_price = "0.00"
            
        # 2. AI: Extract Quote data (Saves quota by only asking for Name and Price)
        try:
            quote = ai_engine.analyze_quote(message.text)
            if quote:
                v_name = quote.get('vendor_name', sender_email)
                v_price = str(quote.get('price', '0.00'))
        except Exception as e:
            print(f"AI Extraction Error (using defaults): {e}")

        # 3. Database: Save this specific vendor's quote
        # Using CURRENT_ITEM ensures all vendor responses match the original Slack request
        db_manager.add_vendor_and_quote(
            v_name=v_name,
            v_email=sender_email,
            item=CURRENT_ITEM,
            price=v_price,
            suggestion=quote.get('suggestion', 'Manual review') if quote else "Quota Limit",
            confidence=quote.get('confidence', 0.0) if quote else 0.0,
            link="N/A"
        )
        print(f"Processed: {CURRENT_ITEM} from {v_name}")

        # 4. FETCH ALL: Get EVERY quote for this item currently in the DB
        all_quotes = db_manager.fetch_data_by_keyword(CURRENT_ITEM)

        # 5. UI: Generate the table using caspian_logic.py
        summary_message = caspian_logic.generate_comparison_table(all_quotes)

        # 6. SLACK: Send the table using your requested try/except block
        if SLACK_CHAT_ID:
            try:
                client.send_message(
                    conversation_id=SLACK_CHAT_ID,
                    text=summary_message
                )
                print(f"Comparison table sent to Slack for {len(all_quotes)} vendors")
            except Exception as e:
                print(f"Slack Send Error: {e}")
