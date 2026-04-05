import sqlite3
class DataB:
	def __init__(self):
		self.conn=sqlite3.connect('chat.db',check_same_thread=False)
		self.cursor=self.conn.cursor()
		self.Ct()
	def Ct(self):
		self.cursor.execute('''CREATE TABLE IF NOT EXISTS chat(id INTEGER PRIMARY KEY,
		name TEXT,
		msg TEXT) ''')
		self.conn.commit()
	def sv(self,name,msg):
		self.cursor.execute('INSERT INTO chat(name, msg)VALUES(?,?)',(name, msg)
		)
		self.conn.commit()
	def sh(self):
		self.cursor.execute('SELECT name,msg FROM chat')
		return self.cursor.fetchall()
