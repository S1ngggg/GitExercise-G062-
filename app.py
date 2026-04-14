from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


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

    cursor.execute(
        "INSERT OR IGNORE INTO category (name) VALUES ('Electronics')")
    cursor.execute("INSERT OR IGNORE INTO category (name) VALUES ('Books')")
    cursor.execute(
        "INSERT OR IGNORE INTO category (name) VALUES ('Furniture')")

    cursor.execute(
        "INSERT INTO item (title,description,category_id,price,status) VALUES ('Computer', 'Brand new fr', 1 , 2000, 'Reserved')")

    cursor.execute("SELECT * FROM category")
    categories = cursor.fetchall()
    print("category:", categories)

    cursor.execute("SELECT * FROM item")
    items = cursor.fetchall()
    print("Items:", items)
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
