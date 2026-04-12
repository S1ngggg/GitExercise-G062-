from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


def create_database():
    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()

    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS item(
                   id INTEGER PRIMARY KEY,
                   name TEXT,
                   description TEXT, 
                   price REAL, 
                   status TEXT
                   
                   )
                   """)

    connect.commit()
    connect.close()


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    create_database()
    app.run(debug=True)
