import sqlite3

def init_db():
    # Connect to (or create) the database file
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    # Create Vendors Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')

    # Create Quotes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_id INTEGER,
            item_name TEXT,
            price REAL,
            suggestion TEXT,
            FOREIGN KEY (vendor_id) REFERENCES vendors (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database and Tables created successfully!")

if __name__ == "__main__":
    init_db()
