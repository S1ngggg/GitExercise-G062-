# import tools for handling form data and page navigation
from flask import request, redirect, url_for, flash, session
from flask import Flask, render_template
from flask_mail import Mail, Message    
import random
from datetime import datetime, timedelta
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__, template_folder='templates',
            static_folder='static', static_url_path='/')

app.config['MAIL_SERVER'] = 'smtp.gmail.com' #configure mail server, here using gmail
app.config['MAIL_PORT'] = 587   #configure mail port, 587 is commonly used for secure email submission
app.config['MAIL_USE_TLS'] = True #enable secure email encryption
app.config['MAIL_USERNAME'] = 'valorantsing2007@gmail.com' 
app.config['MAIL_PASSWORD'] = 'idzw zprj hqak xypr' #use app password for security, generate from google account setting

mail = Mail(app) #initialize flask-mail, connect to flaskapp

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
                   CREATE TABLE IF NOT EXISTS item_condition(
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
                   status_id INTEGER NOT NULL,
                   condition_id INTEGER,
                   price REAL NOT NULL,
                   FOREIGN KEY(category_id) REFERENCES category(id),
                   FOREIGN KEY(status_id) REFERENCES status(id),
                   FOREIGN KEY(condition_id) REFERENCES item_condition(id)
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

    cursor.execute(
        "INSERT OR IGNORE INTO item_condition(name) VALUES ('New')")
    cursor.execute(
        "INSERT OR IGNORE INTO item_condition(name) VALUES ('Like New')")
    cursor.execute(
        "INSERT OR IGNORE INTO item_condition(name) VALUES ('Used')")
    cursor.execute(
        "INSERT OR IGNORE INTO item_condition(name) VALUES ('Heavily Used')")

    cursor.execute("PRAGMA table_info(item)")
    item_columns = [column[1] for column in cursor.fetchall()]
    if "condition_id" not in item_columns:
        cursor.execute("ALTER TABLE item ADD COLUMN condition_id INTEGER")
        cursor.execute("SELECT id FROM item_condition WHERE name = 'Used'")
        default_condition = cursor.fetchone()
        if default_condition:
            cursor.execute(
                "UPDATE item SET condition_id = ? WHERE condition_id IS NULL",
                (default_condition[0],))

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
# required for session + flash
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

        # get all column from user table and then check if the email and username already exist
        cursor.execute(
            """SELECT * FROM user WHERE email = ? OR username = ?""", (email, username))
        user = cursor.fetchone()  # get result from database

        # if user exist redirect to login page
        if user:
            flash("Email or username already exists. Please Login!")
            return redirect(url_for('login'))

        # hash password befor storing into databse
        hashed_password = generate_password_hash(password)

        # inseert new user using hashed_password
        cursor.execute("""
            INSERT INTO user (email, username, password, gender, role)
            VALUES(?, ?, ?, ?, ?)
            """, (email, username, hashed_password, gender, role))  # insert user data using ?

        conn.commit()  # save change to the database
        conn.close()

        # after successful jump to login page
        flash("Register successful! Please login.")
        return redirect(url_for('login'))

    return render_template("register.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    # IF ALREADY LOGGED IN REDIRECT TO HOME
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # serching user by email
        cursor.execute("""SELECT id, email, password FROM user WHERE email =?""", (email,))
        user = cursor.fetchone()
        conn.close()

        # if user not found
        if not user:
            flash("Invalid email or password")
            return redirect(url_for('login'))

        # split database result into separate variable
        user_id, user_email, stored_password = user

        # compare hashed password from database with user input
        if check_password_hash(stored_password, password):
            # create session, store user identity in session
            # remember which user is logged in by storing user id in session
            session['user_id'] = user_id 
            session['email'] = user_email

            return redirect(url_for('home_page'))
        else:
            flash("Invalid email or password")
            return redirect(url_for('login'))

    return render_template("login.html")


@app.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():

    # check whether user submit the form
    if request.method == 'POST':
        email = request.form['email']

        conn = sqlite3.connect('database.db')
        # create cursor to execute sql commands
        cursor = conn.cursor()

        cursor.execute(  # check user email in database
            "SELECT * FROM user WHERE email =?",
            (email,)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            otp = str(random.randint(100000, 999999)) #generate random 6 digit otp
            session['otp'] = otp #store otp in session to compare later
            session['otp_expiry'] = (datetime.now() + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S') #set otp expiry time to 10 minutes

            session['reset_email'] = email #store email in session to identify which user is resetting password
            msg = Message("Password Reset OTP", sender=app.config['MAIL_USERNAME'], recipients=[email]) #create email message
            msg.html = f"""
<html>
    <body>
        <p>Dear {user[2]},</p>

        <p>🔐Your One-Time Password (OTP) is:</p>

        <h3><b>{otp}</b></h3>
        
        <p>It will expire in 10 minutes.</p>
            
        <p>Thank you.</p>
    </body>
</html>"""
            mail.send(msg) 

            flash("OTP sent to your email. Please check your inbox.")
            return redirect(url_for('check_otp')) #redirect to check otp page 

        else:
            flash("Email not found. Please enter a valid email.")
            return redirect(url_for('forgot_password'))
    return render_template("forgot_password.html")


@app.route("/check-otp", methods=['GET','POST'])
def check_otp():
    if request.method == 'POST' :

        user_otp = request.form['otp']
        stored_otp = session.get('otp')
        expiry_time = session.get('otp_expiry')

        #session expired or no otp in session
        if not stored_otp or not expiry_time:
            flash("No OTP found. Please request a new OTP.")
            return redirect(url_for('forgot_password'))
        
        #otp expired
        if datetime.now() > datetime.strptime(expiry_time, '%Y-%m-%d %H:%M:%S'):
            flash("OTP has expired. Please request a new OTP.")
            return redirect(url_for('forgot_password'))
        #otp correct
        if user_otp ==stored_otp:
            #clear otp after success verify
            session.pop('otp', None)
            session.pop('otp_expiry', None)
            flash("OTP verified. Please reset your password.")
            #redirect to reset password page and pass email to identify which user is resetting password
            return redirect(url_for('reset_password',email=session.get('reset_email'))) 
        
        else:
            flash("Invalid OTP. Please try again.")
            return redirect(url_for('check_otp'))
            
    return render_template("check-otp.html")


@app.route("/reset_password/<email>", methods=['GET', 'POST'])
def reset_password(email):
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_new_password']

        if new_password != confirm_password:
            flash("Passwords do not match.")
            # keep the email in the url again after redirect
            return redirect(url_for('reset_password', email=email))

        # update new password in db
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # witout hashing password password store in plain text
        password = generate_password_hash(new_password)
        cursor.execute(
            "UPDATE user SET password = ? WHERE email = ?", (password, email))
        conn.commit()
        conn.close()

        flash("Password reset successful. Please login.")

        return redirect(url_for('login'))

    # pass email to reset password page to identify which user is resetting password
    return render_template("reset_password.html", email=email)


@app.route("/home")
def home_page():
    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()

    cursor.execute("""
        SELECT item.title, item.description, item.price, 
               category.name, status.condition 
        FROM item
        JOIN category ON item.category_id = category.id
        JOIN status ON item.status_id = status.id
    """)

    items_list = cursor.fetchall()
    connect.close()

    return render_template("home.html", items=items_list)


@app.route("/admin")
def admin_dashboard():
    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()

    cursor.execute("SELECT COUNT(*) FROM user")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM item")
    total_listings = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM item
        JOIN status ON item.status_id = status.id
        WHERE status.condition = 'Available'
    """)
    available_listings = cursor.fetchone()[0]

    connect.close()

    stats = {
        "total_users": total_users,
        "total_listings": total_listings,
        "available_listings": available_listings
    }

    return render_template("admin.html", stats=stats)


@app.route("/marketplace", methods=['GET'])
def marketplace():
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    status = request.args.get("status", "").strip()
    condition = request.args.get("condition", "").strip()
    min_price = request.args.get("min_price", "").strip()
    max_price = request.args.get("max_price", "").strip()
    sort = request.args.get("sort", "newest").strip()

    sort_options = {
        "newest": {
            "label": "Newest first",
            "order_by": "item.id DESC"
        },
        "price_low": {
            "label": "Price: Low to High",
            "order_by": "item.price ASC"
        },
        "price_high": {
            "label": "Price: High to Low",
            "order_by": "item.price DESC"
        },
        "title_az": {
            "label": "Title: A to Z",
            "order_by": "item.title ASC"
        }
    }
    if sort not in sort_options:
        sort = "newest"

    connect = sqlite3.connect("database.db")
    cursor = connect.cursor()

    cursor.execute("SELECT * FROM category")
    categories_list = cursor.fetchall()

    cursor.execute("SELECT * FROM status")
    status_list = cursor.fetchall()

    cursor.execute("SELECT * FROM item_condition")
    conditions_list = cursor.fetchall()

    category_names = {str(row[0]): row[1] for row in categories_list}
    status_names = {str(row[0]): row[1] for row in status_list}
    condition_names = {str(row[0]): row[1] for row in conditions_list}

    if category and category not in category_names:
        category = ""
    if status and status not in status_names:
        status = ""
    if condition and condition not in condition_names:
        condition = ""

    query = """
            SELECT item.id, item.title, item.description, item.price,
                   category.name, status.condition,
                   COALESCE(item_condition.name, 'Not specified')
            FROM item
            JOIN category ON item.category_id = category.id
            JOIN status ON item.status_id = status.id
            LEFT JOIN item_condition ON item.condition_id = item_condition.id
            WHERE 1 = 1
            """
    values = []

    if search:
        query += """
                 AND (
                     item.title LIKE ?
                     OR item.description LIKE ?
                     OR category.name LIKE ?
                     OR status.condition LIKE ?
                     OR item_condition.name LIKE ?
                 )
                 """
        search_value = "%" + search + "%"
        values.extend([search_value, search_value, search_value,
                       search_value, search_value])

    if category:
        query += " AND item.category_id = ?"
        values.append(category)

    if status:
        query += " AND item.status_id = ?"
        values.append(status)

    if condition:
        query += " AND item.condition_id = ?"
        values.append(condition)

    min_price_value = None
    max_price_value = None

    if min_price:
        try:
            min_price_value = float(min_price)
            if min_price_value < 0:
                min_price_value = None
                min_price = ""
        except ValueError:
            min_price = ""

    if max_price:
        try:
            max_price_value = float(max_price)
            if max_price_value < 0:
                max_price_value = None
                max_price = ""
        except ValueError:
            max_price = ""

    if min_price_value is not None and max_price_value is not None and min_price_value > max_price_value:
        min_price_value, max_price_value = max_price_value, min_price_value
        min_price, max_price = max_price, min_price

    if min_price_value is not None:
        query += " AND item.price >= ?"
        values.append(min_price_value)

    if max_price_value is not None:
        query += " AND item.price <= ?"
        values.append(max_price_value)

    query += " ORDER BY " + sort_options[sort]["order_by"]

    cursor.execute(query, values)
    items = cursor.fetchall()
    connect.close()

    active_params = {}
    if search:
        active_params["search"] = search
    if category:
        active_params["category"] = category
    if status:
        active_params["status"] = status
    if condition:
        active_params["condition"] = condition
    if min_price:
        active_params["min_price"] = min_price
    if max_price:
        active_params["max_price"] = max_price
    if sort != "newest":
        active_params["sort"] = sort

    active_filters = []

    def add_active_filter(key, label, value):
        remove_params = active_params.copy()
        remove_params.pop(key, None)
        active_filters.append({
            "label": label,
            "value": value,
            "remove_url": url_for("marketplace", **remove_params)
        })

    if search:
        add_active_filter("search", "Keyword", search)
    if category:
        add_active_filter("category", "Category", category_names[category])
    if status:
        add_active_filter("status", "Status", status_names[status])
    if condition:
        add_active_filter("condition", "Condition", condition_names[condition])
    if min_price:
        add_active_filter("min_price", "Min price", "RM " + min_price)
    if max_price:
        add_active_filter("max_price", "Max price", "RM " + max_price)
    if sort != "newest":
        add_active_filter("sort", "Sort", sort_options[sort]["label"])

    return render_template("marketplace.html",
                           items=items,
                           categories=categories_list,
                           status=status_list,
                           conditions=conditions_list,
                           sort_options=sort_options,
                           active_filters=active_filters,
                           search=search,
                           selected_category=category,
                           selected_status=status,
                           selected_condition=condition,
                           min_price=min_price,
                           max_price=max_price,
                           selected_sort=sort)


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
        condition = request.form['condition']

        cursor.execute("""
                       INSERT INTO item(title, description, category_id, status_id, condition_id, price)
                       VALUES(?,?,?,?,?,?)
                       """, (title, description, category, status, condition, price))
        connect.commit()
        connect.close()
        return render_template("item_saved.html")

    # getting all the categories
    cursor.execute("SELECT * FROM category")
    categories_list = cursor.fetchall()

    # getting all statuses
    cursor.execute("SELECT * FROM status")
    status_list = cursor.fetchall()

    cursor.execute("SELECT * FROM item_condition")
    conditions_list = cursor.fetchall()
    connect.close()

    return render_template("item_form.html", categories=categories_list, status=status_list, conditions=conditions_list)


@app.route("/item_saved")
def item_saved():
    return render_template("item_saved.html")


if __name__ == "__main__":
    create_database()
    app.run(debug=True,host='0.0.0.0')
