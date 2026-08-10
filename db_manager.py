import sqlite3

DB_NAME = "inventory.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute('''CREATE TABLE IF NOT EXISTS vendors (
                        vendor_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        name TEXT NOT NULL, 
                        email TEXT UNIQUE NOT NULL)''')

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
                        UNIQUE(v_id, item))''') 
    conn.commit()
    conn.close()

def add_vendor_and_quote(v_name, v_email, item, price, suggestion, confidence, link):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO vendors (name, email) VALUES (?, ?)", (v_name, v_email))
        cursor.execute("SELECT vendor_id FROM vendors WHERE email = ?", (v_email,))
        vendor_id = cursor.fetchone()[0]
        cursor.execute('''INSERT OR REPLACE INTO quotes 
                          (v_id, item, price, suggestion, confidence, email_link, status) 
                          VALUES (?, ?, ?, ?, ?, ?, 'Pending')''', 
                       (vendor_id, item, price, suggestion, confidence, link))
        conn.commit()
    except Exception as e:
        print(f"Error during DB operation: {e}")
    finally:
        conn.close()

def fetch_data_by_keyword(keyword):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # JOIN with vendors table to get the vendor name (q[1])
    query = """
        SELECT q.quote_id, v.name, v.email, q.item, q.price 
        FROM quotes q 
        JOIN vendors v ON q.v_id = v.vendor_id 
        WHERE q.item LIKE ?
    """
    cursor.execute(query, (f"%{keyword}%",))
    results = cursor.fetchall()
    conn.close()
    return results # Returns a list of tuples [(1, 'TechFlow', 'email', 'desktops', 500.0)]
