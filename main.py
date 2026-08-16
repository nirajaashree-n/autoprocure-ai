import ai_engine
import caspian_logic
import db_manager
import os
import time

EMAIL_CONN_ID = "conn_fc1c04a1ab7bc0fa9e28a802"
SLACK_CHAT_ID = None
CURRENT_ITEM = "Requested Item"

VENDORS = ["n.builds.dev@gmail.com", "n.projects.dev@gmail.com"]

def coordinate_flow(message, client, gemini_key=None):
    global SLACK_CHAT_ID, EMAIL_CONN_ID, CURRENT_ITEM

    if gemini_key:
        os.environ["GEMINI_API_KEY"] = gemini_key

    is_email = hasattr(message, 'subject') and message.subject is not None

    if not is_email:
        # --- OWNER REQUEST ---
        SLACK_CHAT_ID = message.conversation_id
        intent = ai_engine.extract_search_intent(message.text)
        CURRENT_ITEM = intent.get("search_term", "items")
        message.reply(f"Analyzing your request for *{CURRENT_ITEM}*...")

        db_manager.init_db()
        for v_email in VENDORS:
            time.sleep(2)
            draft = ai_engine.draft_vendor_email("Supplier", CURRENT_ITEM, "Multiple", message.text)
            client.initiate(
                connection_id=EMAIL_CONN_ID,
                recipient=v_email,
                text=f"Subject: {draft.get('subject')}\n\n{draft.get('body')}"
            )
        print(f"RFQs sent out for: {CURRENT_ITEM}")

    else:
        # --- VENDOR REPLY ---
        sender_email = message.sender.get('address') if isinstance(message.sender, dict) else str(message.sender)
        quote = {"vendor_name": "Vendor", "price": "0.00", "suggestion": "Extraction failed", "confidence": 0}
        v_name = "Vendor"

        try:
            temp_path = None
            if hasattr(message, 'attachments') and message.attachments:
                temp_path = f"temp_{int(time.time())}.pdf"
                with open(temp_path, "wb") as f:
                    f.write(message.attachments[0].content)

            ai_res = ai_engine.analyze_quote(email_text=message.text, file_path=temp_path)
            if ai_res:
                quote = ai_res
                v_name = quote.get('vendor_name', sender_email)

            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception as e:
            print(f"Flow Error: {e}")

        # --- NEW: PRICE CLEANING LAYER ---
        # Converts "Rs 75,00,000" or "7,500.50" to "7500000" or "7500.50"
        raw_price = str(quote.get('price', '0.00'))
        # Keeps only digits and the decimal point
        v_price = "".join(c for c in raw_price if c.isdigit() or c == '.')
        if not v_price: v_price = "0.00"
        # --------------------------------

        try:
            client.initiate(
                connection_id=EMAIL_CONN_ID,
                recipient=sender_email,
                text=(
                    f"Subject: Receipt Acknowledged: Quote for {CURRENT_ITEM}\n\n"
                    f"Hi,\n\n"
                    f"Thank you for submitting your quote for {CURRENT_ITEM}. "
                    f"We have received your pricing and our team is currently reviewing it.\n\n"
                    f"Best regards,\nProcurement Team"
                )
            )
        except Exception as e:
            print(f"Failed to send thank you email: {e}")

        db_manager.add_vendor_and_quote(
            v_name=v_name,
            v_email=sender_email,
            item=CURRENT_ITEM,
            price=v_price, # Using the cleaned price here
            suggestion=quote.get('suggestion', 'Review required'),
            confidence=quote.get('confidence', 0.0),
            link="N/A"
        )

        all_quotes = db_manager.fetch_data_by_keyword(CURRENT_ITEM)
        summary_message = caspian_logic.generate_comparison_table(all_quotes)

        if SLACK_CHAT_ID:
            try:
                client.send_message(conversation_id=SLACK_CHAT_ID, text=summary_message)
            except Exception as e:
                print(f"Slack Send Error: {e}")

