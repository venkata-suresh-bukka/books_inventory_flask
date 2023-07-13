from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

# Establish MySQL database connection
conn = mysql.connector.connect(
    host='database-3.c41buvs5v5ho.ap-south-1.rds.amazonaws.com',
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

@app.route('/take_books')
def reqbooks():
    return render_template('take_books.html')

@app.route('/req_books', methods=['POST', 'GET'])
def req_books():
    book_name = request.form['book_name']
    stu_id = request.form['stu_id']
    stu_name = request.form['name']
    req_qty = request.form['qty']
    book_name = book_name
    if request.method == 'POST': 
        cursor = conn.cursor()
        is_book_table_empty = cursor.execute("SELECT COUNT(*) FROM books").fetchone()[0]
            
        if is_book_table_empty != 0:
            cursor.execute("SELECT title FROM books")
            title_tpl_of_lst = cursor.fetchall()
            title_lst = [item for tpl in title_tpl_of_lst for item in tpl]

            table_lst_len = len(title_lst)
            if table_lst_len >= 1 and book_name in title_lst:
                return take_book_update(book_name, stu_id, stu_name, req_qty)
            else:
                msg = "Book not found"
                return render_template("result.html", msg=msg)
        else:
            msg = "Table is empty"
            return render_template("result.html", msg=msg)
    
def take_book_update(book_name, stu_id, stu_name, req_qty):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT book_id FROM books WHERE title = %s", (book_name,))
        book_id = cursor.fetchone()[0]

        cursor.execute("SELECT qty FROM books WHERE title = %s", (book_name,))
        book_qty = cursor.fetchone()[0]

        if book_qty < int(req_qty):
            msg = "Sorry, book quantity is not available"
            return render_template("result.html", msg=msg)
        else:
            update_qty = book_qty - int(req_qty)

            cursor.execute("UPDATE books SET qty = %s WHERE book_id = %s", (update_qty, book_id))
            cursor.execute("INSERT INTO students (stu_id, book_id, name, book_taken, qty) VALUES (%s, %s, %s, %s, %s)", 
                (stu_id, book_id, stu_name, book_name, req_qty))
            conn.commit()

            msg = "Book taken"
            return render_template("result.html", msg=msg)
    except:
        msg = "Student already took a book with the same ID. Return the old books before taking a new one."
        return render_template("result.html", msg=msg)

@app.route('/return_books')
def returnbooks():
    return render_template('return_books.html')

@app.route('/book_return', methods=['POST', 'GET'])
def book_return():
    if request.method == "POST":
        book_name = request.form['book_name']
        return_qty = request.form['qty']
        stu_id = request.form['stu_id']
        stu_id = int(stu_id)

        cursor = conn.cursor()
        is_stu_table_empty = cursor.execute("SELECT COUNT(*) FROM students").fetchone()[0]

        if is_stu_table_empty != 0:
            cursor.execute("SELECT title FROM books")
            title_tpl_of_lst = cursor.fetchall()
            title_lst = [item for tpl in title_tpl_of_lst for item in tpl] 

            stu_id_check = cursor.execute("SELECT stu_id FROM students").fetchall()
            stu_id_check = [item for tpl in stu_id_check for item in tpl]

            if stu_id in stu_id_check:
                if book_name in title_lst:
                    return return_book_update(book_name, stu_id, return_qty)
                else:
                    msg = "Book not found"
                    return render_template("result.html", msg=msg)
            else:
                msg = "This student does not have any books!"
                return render_template("result.html", msg=msg)
        else:
            msg = "No books have been taken yet!"
            return render_template("result.html", msg=msg)

def return_book_update(book_name, stu_id, return_qty):
    cursor = conn.cursor()    
    stu_id = int(stu_id)
    is_ret_book_avail_str = ""

    cursor.execute("SELECT book_taken FROM students WHERE stu_id = %s", (stu_id,))
    is_ret_book_avail = cursor.fetchone()
    for item in is_ret_book_avail:
        is_ret_book_avail_str += item

    if is_ret_book_avail_str == book_name: 
        cursor.execute("SELECT qty FROM students WHERE stu_id = %s", (stu_id,))
        stu_avail_book_qty = cursor.fetchone()[0]

        if int(return_qty) > stu_avail_book_qty:
            msg = "Student does not have enough books to return"
            return render_template("result.html", msg=msg)
        else:     
            msg = "Book returned"                       
            stu_update_qty = stu_avail_book_qty - int(return_qty)
            cursor.execute("UPDATE students SET qty = %s WHERE stu_id = %s", (stu_update_qty, stu_id))
            conn.commit()            

            cursor.execute("SELECT qty FROM books WHERE title = %s", (book_name,))
            book_avail_book_qty = cursor.fetchone()[0]
                                                
            update_qty = book_avail_book_qty + int(return_qty)
            cursor.execute("UPDATE books SET qty = %s WHERE title = %s", (update_qty, book_name))
            conn.commit()

            return render_template("result.html", msg=msg)
    else:
        msg = "This student does not have this book"
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
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()
    print(rows)
    return render_template("list_books.html", rows=rows)

if __name__ == "__main__":
    app.run(debug=True)
    conn.close()
