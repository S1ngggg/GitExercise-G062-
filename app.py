# import tools for handling form data and page navigation
from flask import request, redirect, url_for, flash, session
from flask import Flask, render_template
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__, template_folder='templates',
            static_folder='static', static_url_path='/')


# Creating the tables

def create_database():
    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()

    cursor.execute("""

                   CREATE TABLE IF NOT EXISTS category(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL UNIQUE
                   
                   )
                   """)

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS status(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   condition TEXT NOT NULL UNIQUE
                   
                   )
                   """)

    cursor.execute("""


                   CREATE TABLE IF NOT EXISTS item(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   title TEXT NOT NULL,
                   description TEXT NOT NULL,
                   category_id INTEGER NOT NULL,
                   status_id INTEGER NOT NULL,
                   price REAL NOT NULL,
                   FOREIGN KEY(category_id) REFERENCES category(id),
                   FOREIGN KEY(status_id) REFERENCES status(id)
                   )
                   """)

    # Adding default categories

    cursor.execute(
        "INSERT OR IGNORE INTO category (name) VALUES ('Electronics')")
    cursor.execute("INSERT OR IGNORE INTO category (name) VALUES ('Books')")
    cursor.execute(
        "INSERT OR IGNORE INTO category (name) VALUES ('Furniture')")
    cursor.execute(
        "INSERT OR IGNORE INTO category (name) VALUES ('Second-hand')")
   # Adding default and possibly permanent status conditions

    cursor.execute("INSERT OR IGNORE INTO status(condition) VALUES ('Sold')")
    cursor.execute(
        "INSERT OR IGNORE INTO status(condition) VALUES ('Reserved')")
    cursor.execute(
        "INSERT OR IGNORE INTO status(condition) VALUES ('Available')")

    # create user table if does not exist yet
    cursor.execute("""
                   
                CREATE TABLE IF NOT EXISTS user(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                gender TEXT NOT NULL,
                role TEXT NOT NULL
                )

                """)

    connect.commit()  
    connect.close()


@app.route("/")
def home():
    return render_template("index.html")

app.secret_key = "my_secret_key......"
#required for session + flash
# accept displaying form and processing form
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':  # if user submit form
        email = request.form['email']  # data from frontend
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        gender = request.form['gender']
        role = request.form['role']

        if password != confirm_password:
            flash("Password not match")
            return render_template("register.html")

        conn = sqlite3.connect('database.db')  # connect to sqlite database
        cursor = conn.cursor()

        #get all column from user table and then check if the email and username already exist
        cursor.execute("""SELECT * FROM user WHERE email = ? OR username = ?""", (email,username))
        user= cursor.fetchone()#get result from database

        #if user exist redirect to login page
        if user:
            flash("Email or username already exists. Please Login!")
            return redirect(url_for('login'))
        
        #hash password befor storing into databse
        hashed_password= generate_password_hash(password)
        
        #inseert new user using hashed_password
        cursor.execute("""
            INSERT INTO user (email, username, password, gender, role)
            VALUES(?, ?, ?, ?, ?)
            """, (email, username, hashed_password, gender, role))  # insert user data using ?

        conn.commit() # save change to the database
        conn.close()

        # after successful jump to login page
        flash("Register successful! Please login.")
        return redirect(url_for('login'))

    return render_template("register.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    #IF ALREADY LOGGED IN REDIRECT TO HOME
    if 'user_id' in session :
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        #serching user by email
        cursor.execute("""SELECT id, email, password FROM user WHERE email =?""", (email,))
        user=cursor.fetchone()
        conn.close()

        #if user not found
        if not user:
            flash("Invalid email or password")
            return redirect(url_for('login'))
        
        user_id, user_email, stored_password = user #split database result into separate variable
        
        #compare hashed password from database with user input
        if check_password_hash(stored_password, password):
            session['user_id'] = user_id#create session, store user identity in session
            session['email'] = user_email

            return redirect(url_for('home_page'))
        else:
            flash("Invalid email or password")
            return redirect(url_for('login'))
    return render_template("login.html")


@app.route("/home")
def home_page():
    return render_template("home.html")


@app.route("/marketplace", methods=['GET'])
def marketplace():
    search = request.args.get("search", "")
    category = request.args.get("category", "")
    status = request.args.get("status", "")

    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()

    cursor.execute("SELECT * FROM category")
    categories_list = cursor.fetchall()

    cursor.execute("SELECT * FROM status")
    status_list = cursor.fetchall()

    query = """
            SELECT item.title, item.description, item.price, category.name, status.condition
            FROM item
            JOIN category ON item.category_id = category.id
            JOIN status ON item.status_id = status.id
            WHERE 1 = 1
            """
    values = []

    if search:
        query += " AND (item.title LIKE ? OR item.description LIKE ?)"
        values.append("%" + search + "%")
        values.append("%" + search + "%")

    if category:
        query += " AND item.category_id = ?"
        values.append(category)

    if status:
        query += " AND item.status_id = ?"
        values.append(status)

    cursor.execute(query, values)
    items = cursor.fetchall()
    connect.close()

    return render_template("marketplace.html",
                           items=items,
                           categories=categories_list,
                           status=status_list,
                           search=search,
                           selected_category=category,
                           selected_status=status)


@app.route("/item_form", methods=['GET', 'POST'])
def item_form():
    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()

    if request.method == 'POST':

        title = request.form["title"]
        description = request.form["description"]
        price = request.form['price']
        category = request.form['category']
        status = request.form['status']

        cursor.execute("""
                       INSERT INTO item(title, description, category_id, status_id, price)
                       VALUES(?,?,?,?,?)
                       """, (title, description, category, status, price))
        connect.commit()
        connect.close()
        return "Item saved"

    # getting all the categories
    cursor.execute("SELECT * FROM category")
    categories_list = cursor.fetchall()

    # getting all statuses
    cursor.execute("SELECT * FROM status")
    status_list = cursor.fetchall()
    connect.close()

    return render_template("item_form.html", categories=categories_list, status=status_list)


if __name__ == "__main__":
    create_database()
    app.run(debug=True)
