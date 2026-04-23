from flask import Flask,render_template
import sqlite3

app = Flask(__name__,template_folder='templates',static_folder='static',static_url_path='/')


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


                   CREATE TABLE IF NOT EXISTS item(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   title TEXT NOT NULL,
                   description TEXT NOT NULL,
                   category_id INTEGER NOT NULL,
                   price REAL NOT NULL,
                   status TEXT NOT NULL,
                   FOREIGN KEY(category_id) REFERENCES category(id)

                   )
                   """)
    #create user table if does not exist yet
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

    connect.commit()#save change to the database
    connect.close()


@app.route("/")
def home():
    return render_template("index.html")

from flask import request, redirect, url_for #import tools for handling form data and page navigation

@app.route("/register", methods=['GET','POST'])#accept displaying form and processing form
def register():
    if request.method == 'POST':#if user submit form
        email = request.form['email']#data from frontend
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        gender = request.form['gender']
        role = request.form['role']

        if password != confirm_password:
            return "Password not match"


        conn = sqlite3.connect('database.db')#connect to sqlite database
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO user (email, username, password, gender, role)
            VALUES(?, ?, ?, ?, ?)
            """,(email, username, password, gender, role)) #insert user data using ? 
        
        conn.commit()
        conn.close()

        return redirect(url_for('login'))#after form submitted jump to login page
    
    return render_template("register.html")

@app.route("/login")
def login() :
    return render_template("login.html")


@app.route("/home")
def home_page():
    return render_template("home.html")


if __name__ == "__main__":
    create_database()
    app.run(debug=True)
