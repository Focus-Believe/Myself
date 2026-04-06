import sqlite3
import os
import psycopg2

class DataB:
    def __init__(self):
        self.db_url = os.environ.get('DATABASE_URL')

        try:
            if self.db_url:
                # PostgreSQL (Render)
                self.conn = psycopg2.connect(self.db_url, sslmode='require')
                self.is_postgres = True
            else:
                # SQLite (Local)
                self.conn = sqlite3.connect('chat.db', check_same_thread=False)
                self.is_postgres = False

            self.cursor = self.conn.cursor()
            self.Ct()

        except Exception as e:
            print("❌ DB Connection Error:", e)

    # ----------------------------
    # Create Table
    # ----------------------------
    def Ct(self):
        try:
            if self.is_postgres:
                query = '''CREATE TABLE IF NOT EXISTS chat(
                            id SERIAL PRIMARY KEY,
                            name TEXT,
                            msg TEXT)'''
            else:
                query = '''CREATE TABLE IF NOT EXISTS chat(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT,
                            msg TEXT)'''

            self.cursor.execute(query)
            self.conn.commit()

        except Exception as e:
            print("❌ Table Error:", e)

    # ----------------------------
    # Save (same name: sv)
    # ----------------------------
    def sv(self, name, msg):
        try:
            if self.is_postgres:
                self.cursor.execute(
                    'INSERT INTO chat(name, msg) VALUES(%s, %s)',
                    (name, msg)
                )
            else:
                self.cursor.execute(
                    'INSERT INTO chat(name, msg) VALUES(?, ?)',
                    (name, msg)
                )

            self.conn.commit()

        except Exception as e:
            print("❌ Insert Error:", e)

    # ----------------------------
    # Show (same name: sh)
    # ----------------------------
    def sh(self):
        try:
            self.cursor.execute('SELECT name, msg FROM chat ORDER BY id DESC')
            return self.cursor.fetchall()

        except Exception as e:
            print("❌ Fetch Error:", e)
            return []

    # ----------------------------
    # Close (optional)
    # ----------------------------
    def close(self):
        try:
            self.conn.close()
        except:
            pass
