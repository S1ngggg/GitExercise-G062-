# import tools for handling form data and page navigation
from flask import request, redirect, url_for
from flask import Flask, render_template
import sqlite3

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

    connect.commit()  # save change to the database
    connect.close()


@app.route("/")
def home():
    return render_template("index.html")


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
            return "Password not match"

        conn = sqlite3.connect('database.db')  # connect to sqlite database
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO user (email, username, password, gender, role)
            VALUES(?, ?, ?, ?, ?)
            """, (email, username, password, gender, role))  # insert user data using ?

        conn.commit()
        conn.close()

        # after form submitted jump to login page
        return redirect(url_for('login'))

    return render_template("register.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/home")
def home_page():
    return render_template("home.html")


@app.route("/marketplace")
def marketplace():
    return render_template("marketplace.html")


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
