import sqlite3

class Memory:
    def __init__(self, db_path="memory/agent_memory.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT,
            response TEXT
        )
        """)

    def save(self, prompt, response):
        self.conn.execute("INSERT INTO memory (prompt, response) VALUES (?, ?)", (prompt, response))
        self.conn.commit()

    def fetch_all(self):
        cursor = self.conn.execute("SELECT * FROM memory")
        return cursor.fetchall()
