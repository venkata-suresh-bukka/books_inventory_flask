import sqlite3

conn = sqlite3.connect('book_database.db')
print("opened db successfully")

conn.execute("CREATE TABLE books(book_id INTEGER,author TEXT,title TEXT,qty INTEGER)")
conn.execute("CREATE TABLE students(stu_id INTEGER,book_id INTEGER,name TEXT,book_taken TEXT,qty INTEGER)")
print("table created")

conn.close()