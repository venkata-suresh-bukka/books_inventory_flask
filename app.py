from  flask import Flask, render_template, request
import sqlite3 as sql
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/add_book')
def newbook():
    return render_template('add_book.html')

@app.route('/new_book',methods = ['POST','GET'])
def new_book():
    if request.method == 'POST':
        try:
            book_id = request.form['book_id']
            author = request.form['author']
            title = request.form['title']
            qty = request.form['qty']
            with sql.connect('book_database.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO books (book_id,author,title,qty) VALUES (?,?,?,?)", (book_id,author,title,qty))                       
                con.commit()
                msg = "book added"
                return render_template('result.html', msg=msg)
                con.close() 
        except:
            con.rollback()
            msg = "book already exists with same id"
            return render_template('result.html', msg=msg)
            con.close() 


@app.route('/take_books')
def reqbooks():
    return render_template('take_books.html')

@app.route('/req_books',methods=['POST','GET'])
def req_books():
    book_name = request.form['book_name']
    stu_id = request.form['stu_id']
    stu_name = request.form['name']
    req_qty = request.form['qty']
    book_name = book_name
    if request.method == 'POST': 
        conn = sql.connect('book_database.db') 
        cur = conn.cursor()
        is_book_table_empty = cur.execute("SELECT count(*)from books").fetchone()
        is_book_table_empty = [str(integer) for integer in is_book_table_empty]
        a_string = "".join(is_book_table_empty)
        is_book_table_empty = int(a_string)
            
        if is_book_table_empty != 0:
            title_tpl_of_lst = cur.execute("SELECT title from books").fetchall()
            title_lst = [item for t in title_tpl_of_lst for item in t]

            table_lst_len = len(title_lst)
            if table_lst_len == 1:
                if title_lst[0] == book_name:
                    return take_book_update(book_name,stu_id,stu_name,req_qty)
                else:
                    msg = "book not found"
                    return render_template("result.html",msg=msg)

            elif table_lst_len == 2:
                if title_lst[0] == book_name:
                    return take_book_update(book_name,stu_id,stu_name,req_qty)
                elif title_lst[1] == book_name:
                    return take_book_update(book_name,stu_id,stu_name,req_qty)
                else:
                    msg = "book not found"
                    return render_template("result.html",msg=msg)

            elif table_lst_len == 3:
                if title_lst[0] == book_name:
                    return take_book_update(book_name,stu_id,stu_name,req_qty)
                elif title_lst[1] == book_name:
                    return take_book_update(book_name,stu_id,stu_name,req_qty)
                elif title_lst[2] == book_name:
                    return take_book_update(book_name,stu_id,stu_name,req_qty)
                else:
                    msg = "book not found"
                    return render_template("result.html",msg=msg)
        else:
            msg = "table mpty"
            return render_template("result.html",msg=msg)

               
def take_book_update(book_name,stu_id,stu_name,req_qty):   
    conn = sql.connect('book_database.db') 
    cur = conn.cursor()
    try:
        book_id = cur.execute("SELECT book_id from books where title =(?)",[book_name]).fetchone()
        book_id = [str(integer) for integer in book_id]
        a_string = "".join(book_id)
        book_id = int(a_string)

        cur.execute("SELECT qty from books where title = (?)",[book_name])
        quantity = cur.fetchone()
        quantity = [str(integer) for integer in quantity]
        a_string = "".join(quantity)
        book_qty = int(a_string)

        if book_qty < int(req_qty):
            msg = "sorry book quantity is not available" 
            return render_template("result.html",msg=msg)
        else:
            update_qty = book_qty - int(req_qty)
            update_qty = int(update_qty)

            cur.execute("UPDATE books SET qty = (?) WHERE book_id = (?)", (update_qty,book_id))
            cur.execute("INSERT INTO students (stu_id,book_id,name,book_taken,qty) VALUES (?,?,?,?,?)", 
                (stu_id,book_id,stu_name,book_name,req_qty))
            conn.commit()
            msg = "book taken"
            return render_template("result.html",msg=msg)
    except:
        msg = "student alreay taken book with same id return old books"
        return render_template("result.html",msg=msg)

                
            


@app.route('/return_books')
def returnbooks():
    return render_template('return_books.html')

@app.route('/book_return', methods=['POST','GET'])
def book_return():
    conn = sql.connect('book_database.db') 
    if request.method == "POST":
        book_name = request.form['book_name']
        return_qty = request.form['qty']
        stu_id = request.form['stu_id']
        stu_id = int(stu_id)

        conn = sql.connect('book_database.db') 
        cur = conn.cursor()
        is_stu_table_empty = cur.execute("SELECT count(*)from students").fetchone()
        is_stu_table_empty = [str(integer) for integer in is_stu_table_empty]
        a_string = "".join(is_stu_table_empty)
        is_stu_table_empty = int(a_string)

        if is_stu_table_empty != 0:
            title_tpl_of_lst = cur.execute("SELECT title from books").fetchall()
            title_lst = [item for t in title_tpl_of_lst for item in t] 
            title_lst_len = len(title_lst)

            stu_id_check = cur.execute("SELECT stu_id from students").fetchall()
            stu_id_check = [item for t in stu_id_check for item in t]

            stu_id_check = stu_id in stu_id_check

            if stu_id_check == True:
                if title_lst_len == 1:
                    if title_lst[0] == book_name:
                        return return_book_update(book_name,stu_id,return_qty)
                    else:
                        msg = "book not found"
                        return render_template("result.html",msg=msg)

                elif title_lst_len == 2:
                    if title_lst[0] == book_name:
                        return return_book_update(book_name,stu_id,return_qty)
                    elif title_lst[1] == book_name:
                        return return_book_update(book_name,stu_id,return_qty)
                    else:
                        msg = "book not found"
                        return render_template("result.html",msg=msg)

                elif title_lst_len == 3:
                    if title_lst[0] == book_name:
                        return return_book_update(book_name,stu_id_check,return_qty)
                    elif title_lst[1] == book_name:
                        return return_book_update(book_name,stu_id_check,return_qty)
                    elif title_lst[2] == book_name:
                        return return_book_update(book_name,stu_id_check,return_qty)
                    else:
                        msg = "book not found"
                        return render_template("result.html",msg=msg) 
                else:
                    msg = "no one taken book to return!"   
                    return render_template("result.html",msg=msg)           
            else:
                msg = "this stu_id dont have book!"
                return render_template("result.html",msg=msg)
          

def return_book_update(book_name,stu_id,return_qty):
    conn = sql.connect('book_database.db') 
    cur = conn.cursor()    
    stu_id = int(stu_id)
    is_ret_book_avail_str = ""


    is_ret_book_avail = cur.execute("SELECT book_taken from students where stu_id = (?)",(stu_id,)).fetchone()
    for i in is_ret_book_avail:
        is_ret_book_avail_str += i

    if is_ret_book_avail_str == book_name: 
        stu_avail_book_qty = cur.execute("SELECT qty from students where stu_id=(?)",(stu_id,))
        stu_avail_book_qty = cur.fetchone()
        stu_avail_book_qty = [str(integer) for integer in stu_avail_book_qty]
        a_string = "".join(stu_avail_book_qty)
        stu_avail_book_qty = int(a_string)

        if int(return_qty) > stu_avail_book_qty:
            msg = "he dont have enough books to return"
            return render_template("result.html",msg=msg)
        else:     
            msg = "book returned"                       
            stu_update_qty = stu_avail_book_qty - int(return_qty)
            cur.execute("UPDATE students SET qty=(?) where stu_id =(?)", (stu_update_qty,stu_id))
            conn.commit()            
                                                

            book_avail_book_qty = cur.execute("SELECT qty from books where title=(?)", [book_name])
            book_avail_book_qty = cur.fetchone()
            book_avail_book_qty = [str(integer) for integer in book_avail_book_qty]
            a_string = "".join(book_avail_book_qty)
            book_avail_book_qty = int(a_string)
                                                

            update_qty = book_avail_book_qty + int(return_qty)
            update_qty = int(update_qty) 
            cur.execute("UPDATE books SET qty = (?) WHERE title = (?)", (update_qty,book_name))
            conn.commit()

            return render_template("result.html",msg=msg)
            conn.close() 
    else:
        msg = "this stu dont have this book"
        return render_template("result.html",msg=msg)                       


@app.route('/lst_taken_books')
def lst_taken_books():
    con = sql.connect("book_database.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from students")
    rows = cur.fetchall()
    con.execute("DELETE  from students where qty = 0")
    con.commit()
    return render_template("lst_taken_books.html",rows=rows)
    con.close()


@app.route('/list_books')
def list():
    con = sql.connect("book_database.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from books")
    rows = cur.fetchall()
    return render_template("list_books.html",rows=rows)

if __name__ == "__main__":
    app.run(debug=True)