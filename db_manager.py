import sqlite3

DB_NAME = "inventory.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Enable Foreign Key support (must be done per connection)
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 2. Create Vendors Table (The Parent)
    cursor.execute('''CREATE TABLE IF NOT EXISTS vendors (
                        vendor_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        name TEXT NOT NULL, 
                        email TEXT UNIQUE NOT NULL
                    )''')

    # 3. Create Quotes Table (The Child)
    # UNIQUE(v_id, item) ensures a vendor can't have two entries for the same product
    cursor.execute('''CREATE TABLE IF NOT EXISTS quotes (
                        quote_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        v_id INTEGER NOT NULL, 
                        item TEXT NOT NULL, 
                        price REAL, 
                        suggestion TEXT,
                        confidence REAL,
                        email_link TEXT,
                        status TEXT DEFAULT 'Pending',
                        FOREIGN KEY (v_id) REFERENCES vendors(vendor_id),
                        UNIQUE(v_id, item)
                    )''') 
    
    conn.commit()
    conn.close()
    print(" Database initialized with Constraints and Status column.")

def add_vendor_and_quote(v_name, v_email, item, price, suggestion, confidence, link):
    """
    Handles the logic of:
    1. Adding/Finding the Vendor
    2. Adding/Updating the Quote
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    try:
        # Insert vendor if they don't exist, or just get the ID
        cursor.execute("INSERT OR IGNORE INTO vendors (name, email) VALUES (?, ?)", (v_name, v_email))
        cursor.execute("SELECT vendor_id FROM vendors WHERE email = ?", (v_email,))
        vendor_id = cursor.fetchone()[0]

        # Insert or Replace the quote 
        cursor.execute('''INSERT OR REPLACE INTO quotes 
                          (v_id, item, price, suggestion, confidence, email_link, status) 
                          VALUES (?, ?, ?, ?, ?, ?, 'Pending')''', 
                       (vendor_id, item, price, suggestion, confidence, link))
        
        conn.commit()
        print(f" Successfully processed quote for '{item}' from '{v_name}'")
    except Exception as e:
        print(f" Error during DB operation: {e}")
    finally:
        conn.close()

def fetch_data_by_keyword(keyword, search_type="item"):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # This makes the result act like a dictionary!
    cursor = conn.cursor()
    
    if search_type == "id":
        query = "SELECT * FROM quotes WHERE quote_id = ?"
        cursor.execute(query, (keyword,))
    else:
        query = "SELECT * FROM quotes WHERE item LIKE ?"
        cursor.execute(query, (f"%{keyword}%",))
        
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_vendors_for_item(item_keyword):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Find unique vendors who have supplied this item in the past
    query = "SELECT DISTINCT vendor_name, vendor_email FROM quotes WHERE item LIKE ?"
    cursor.execute(query, (f'%{item_keyword}%',))
    vendors = cursor.fetchall()
    conn.close()
    return vendors # Returns a list of tuples: [('Dell', 'sales@dell.com'), ('HP', 'contact@hp.com')]

if __name__ == "__main__":
    init_db()

    # Test saving a fake quote
    add_vendor_and_quote("Test Vendor", "test@v.com", "Laptops", 50000, "Good deal", 0.95, "http://link.com")
    print("Data Saved")
    
    # Test fetching data
    results = fetch_data_by_keyword("Laptops", "item")
    print(f"Fetch Result: {results}")
