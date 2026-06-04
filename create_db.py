import sqlite3

def setup_database():
    conn = None
    try:
        conn = sqlite3.connect("atm.db")
        cur = conn.cursor()

        # Users table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            acc_no TEXT PRIMARY KEY,
            pin TEXT,
            balance REAL
        )
        """)

        # Transactions table to track history
        cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            acc_no TEXT,
            type TEXT,
            amount REAL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(acc_no) REFERENCES users(acc_no)
        )
        """)

        # Insert a sample user
        cur.execute("INSERT OR IGNORE INTO users VALUES ('123456', '1234', 10000.0)")

        conn.commit()
        print("Database initialized successfully with advanced schema.")
        print("Sample Account - Acc No: 123456, PIN: 1234")
        
    except sqlite3.Error as e:
        print(f"An error occurred while creating database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    setup_database()
