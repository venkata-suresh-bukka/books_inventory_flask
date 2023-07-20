import mysql.connector

# Establish a connection to MySQL server
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='admin123',
    database='migration'
)
print("Connected to MySQL database successfully")

# Create the books table
books_table_query = """
CREATE TABLE books (
    book_id INT PRIMARY KEY,
    author VARCHAR(255),
    title VARCHAR(255),
    qty INT
)
"""
conn.cursor().execute(books_table_query)
print("Created books table")

# Create the students table
students_table_query = """
CREATE TABLE students (
    stu_id INT PRIMARY KEY,
    book_id INT,
    name VARCHAR(255),
    book_taken VARCHAR(255),
    qty INT,
    FOREIGN KEY (book_id) REFERENCES books (book_id)
)
"""
conn.cursor().execute(students_table_query)
print("Created students table")

# Close the connection
conn.close()


