from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


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
                   FOREIGN KEY(category_id) REFERENCES category(id)
                   FOREIGN KEY(status_id) REFERENCES status(id)
                   )
                   """)

# Adding default categories

    cursor.execute(
        "INSERT OR IGNORE INTO category (name) VALUES ('Electronics')")
    cursor.execute("INSERT OR IGNORE INTO category (name) VALUES ('Books')")
    cursor.execute(
        "INSERT OR IGNORE INTO category (name) VALUES ('Furniture')")

# Adding default and possibly permanent status conditions

    cursor.execute("INSERT OR IGNORE INTO status(condition) VALUES ('Sold')")
    cursor.execute(
        "INSERT OR IGNORE INTO status(condition) VALUES ('Reserved')")
    cursor.execute(
        "INSERT OR IGNORE INTO status(condition) VALUES ('Available')")

    connect.commit()
    connect.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/home")
def home_page():
    return render_template("home.html")


if __name__ == "__main__":
    create_database()
    app.run(debug=True)
