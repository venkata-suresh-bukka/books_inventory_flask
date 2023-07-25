from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

# Establish MySQL database connection
conn = mysql.connector.connect(
    host='database-1.chgyov1i10un.ap-south-1.rds.amazonaws.com',
    user='admin',
    password='admin123',
    database='healthchecks'
)
print("Connected to MySQL database successfully")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/add_book')
def newbook():
    return render_template('add_book.html')

@app.route('/new_book', methods=['POST', 'GET'])
def new_book():
    if request.method == 'POST':
        try:
            book_id = request.form['book_id']
            author = request.form['author']
            title = request.form['title']
            qty = request.form['qty']
            
            # Execute SQL query to insert a new book into the books table
            cursor = conn.cursor()
            insert_query = "INSERT INTO books (book_id, author, title, qty) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (book_id, author, title, qty))
            conn.commit()
            cursor.close()
            
            msg = "Book added"
            return render_template('result.html', msg=msg)
        except mysql.connector.Error as e:
            conn.rollback()
            msg = "Book already exists with the same ID"
            return render_template('result.html', msg=msg)
    return render_template('add_book.html')

@app.route('/take_books')
def reqbooks():
    return render_template('take_books.html')

@app.route('/req_books', methods=['POST', 'GET'])
def req_books():
    if request.method == 'POST':
        book_name = request.form['book_name']
        stu_id = request.form['stu_id']
        stu_name = request.form['name']
        req_qty = int(request.form['qty'])

        cursor = conn.cursor()

        # Check if the book exists in the database
        cursor.execute("SELECT COUNT(*) FROM books WHERE title = %s", (book_name,))
        book_count = cursor.fetchone()[0]

        if book_count == 0:
            msg = "Book not found"
            return render_template("result.html", msg=msg)

        # Check if the requested quantity is available
        cursor.execute("SELECT qty FROM books WHERE title = %s", (book_name,))
        book_qty = cursor.fetchone()[0]

        if book_qty < req_qty:
            msg = "Sorry, book quantity is not available"
            return render_template("result.html", msg=msg)

        # Update book quantity and add book to students' table
        update_qty = book_qty - req_qty
        cursor.execute("UPDATE books SET qty = %s WHERE title = %s", (update_qty, book_name))
        cursor.execute("INSERT INTO students (stu_id, book_id, name, book_taken, qty) VALUES (%s, (SELECT book_id FROM books WHERE title = %s), %s, %s, %s)",
                       (stu_id, book_name, stu_name, book_name, req_qty))
        conn.commit()

        msg = "Book taken"
        return render_template("result.html", msg=msg)

    return render_template("take_books.html")


def take_book_update(book_name, stu_id, return_qty):
    cursor = conn.cursor()
    stu_id = int(stu_id)

    # Check if the student has borrowed the book
    cursor.execute("SELECT COUNT(*) FROM students WHERE stu_id = %s AND book_taken = %s", (stu_id, book_name))
    book_count = cursor.fetchone()[0]

    if book_count == 0:
        msg = "This student does not have this book"
        return render_template("result.html", msg=msg)

    # Get the current quantity of the book borrowed by the student
    cursor.execute("SELECT qty FROM students WHERE stu_id = %s AND book_taken = %s", (stu_id, book_name))
    stu_avail_book_qty = cursor.fetchone()[0]

    if int(return_qty) > stu_avail_book_qty:
        msg = "Student does not have enough books to return"
        return render_template("result.html", msg=msg)

    # Update student quantity and book quantity
    stu_update_qty = stu_avail_book_qty - int(return_qty)
    cursor.execute("UPDATE students SET qty = %s WHERE stu_id = %s AND book_taken = %s", (stu_update_qty, stu_id, book_name))
    conn.commit()

    cursor.execute("SELECT qty FROM books WHERE title = %s", (book_name,))
    book_avail_book_qty = cursor.fetchone()[0]

    update_qty = book_avail_book_qty + int(return_qty)
    cursor.execute("UPDATE books SET qty = %s WHERE title = %s", (update_qty, book_name))
    conn.commit()

    msg = "Book returned"
    return render_template("result.html", msg=msg)



@app.route('/return_books')
def returnbooks():
    return render_template('return_books.html')

@app.route('/book_return', methods=['POST', 'GET'])
def book_return():
    if request.method == "POST":
        book_name = request.form['book_name']
        return_qty = int(request.form['qty'])
        stu_id = int(request.form['stu_id'])

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM students WHERE stu_id = %s", (stu_id,))
        is_student_exist = cursor.fetchone()[0]

        if is_student_exist == 0:
            msg = "This student does not exist!"
            return render_template("result.html", msg=msg)

        cursor.execute("SELECT COUNT(*) FROM students WHERE stu_id = %s AND book_taken = %s", (stu_id, book_name))
        has_book = cursor.fetchone()[0]

        if has_book == 0:
            msg = "This student does not have this book!"
            return render_template("result.html", msg=msg)

        return return_book_update(book_name, stu_id, return_qty)

    return render_template("return_books.html")

def return_book_update(book_name, stu_id, return_qty):
    cursor = conn.cursor()

    cursor.execute("SELECT qty FROM students WHERE stu_id = %s AND book_taken = %s", (stu_id, book_name))
    stu_avail_book_qty = cursor.fetchone()[0]

    if return_qty > stu_avail_book_qty:
        msg = "Student does not have enough books to return"
        return render_template("result.html", msg=msg)

    # Update student quantity and book quantity
    stu_update_qty = stu_avail_book_qty - return_qty
    cursor.execute("UPDATE students SET qty = %s WHERE stu_id = %s AND book_taken = %s", (stu_update_qty, stu_id, book_name))
    conn.commit()

    cursor.execute("SELECT qty FROM books WHERE title = %s", (book_name,))
    book_avail_book_qty = cursor.fetchone()[0]

    update_qty = book_avail_book_qty + return_qty
    cursor.execute("UPDATE books SET qty = %s WHERE title = %s", (update_qty, book_name))
    conn.commit()

    msg = "Book returned"
    return render_template("result.html", msg=msg)


@app.route('/lst_taken_books')
def lst_taken_books():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    cursor.execute("DELETE FROM students WHERE qty = 0")
    conn.commit()
    return render_template("lst_taken_books.html", rows=rows)

@app.route('/list_books')
def list_books():
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT *from books")
        rows = cursor.fetchall()
        print(rows)
        cursor.close()

        return render_template("list_books.html", rows=rows)
    except mysql.connector.Error as e:
        print("Error fetching data from the database:", e)
        return render_template("error.html")


if __name__ == "__main__":
    app.run(debug=True)
    conn.close()
