from flask import Flask, flash,  request, redirect, url_for, session, render_template
from flask_mysqldb import MySQL
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "lol"

# ✅ MySQL config pulled from environment (Render injects these)
app.config['MYSQL_HOST'] = os.environ.get('host')
app.config['MYSQL_PORT'] = int(os.environ.get('port'))
app.config['MYSQL_USER'] = os.environ.get('user')
app.config['MYSQL_PASSWORD'] = os.environ.get('password')
app.config['MYSQL_DB'] = os.environ.get('schema')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_UNIX_SOCKET'] = None

app.config['TEMPLATES_AUTO_RELOAD'] = True

mysql = MySQL(app)

mysql = MySQL(app)

from Dealer.routes import dealer
from admin.routes import admin
from employee.routes import employee
# Register Blueprints
app.register_blueprint(dealer)
app.register_blueprint(admin)
app.register_blueprint(employee)

# Login Route
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form.get("user_id")
        password = request.form.get("password")

        # Create cursor
        cur = mysql.connection.cursor()
        
        # Execute query - using the users table
        cur.execute("SELECT User_ID, Role, Password FROM users WHERE User_ID=%s", [user_id])
        user = cur.fetchone()
        
        # Close cursor
        cur.close()

        if user:
            # Check if the password is hashed properly or stored as plaintext
            stored_password = user["Password"]
            
            # Try with password hash verification
            if stored_password == password:
                session["user_id"] = user["User_ID"]
                session["role"] = user["Role"]
                flash(f"Login successful! Role: {user['Role']}", "success")
                return redirect(url_for("home"))
            else:
                flash("Invalid password. Please try again!", "danger")
        else:
            flash("User ID not found!", "danger")

    return render_template("login.html")

# Create Account Route
@app.route("/create-account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        phone_no = request.form.get("phoneNo")
        aadhar_no = request.form.get("AadharNo")

        if not all([name, password, phone_no, aadhar_no]):
            flash("All fields are required", "danger")
            return redirect(url_for("create_account"))
        if(len(aadhar_no)!=12):
            flash("Aadhar number should be of length 12", "danger")
            return redirect(url_for("create_account"))
        if(len(phone_no)!=10):
            flash("Phone no. should be of length 10", "danger")
            return redirect(url_for("create_account"))
        try:
            # Create cursor
            cur = mysql.connection.cursor()
            
            # Check if user with this Aadhar already exists
            cur.execute("SELECT * FROM dealer WHERE Aadhar_Number = %s", [aadhar_no])
            existing_user = cur.fetchone()
            
            if existing_user:
                flash("A user with this Aadhar number already exists", "danger")
                return redirect(url_for("create_account"))
            
            # First insert into dealer table
            cur.execute("INSERT INTO users (Role,Name,Password) VALUES (%s,%s,%s)",["Dealer",name,password])
            cur.execute("SELECT LAST_INSERT_ID()")
            dealer_id = cur.fetchone()['LAST_INSERT_ID()']
            cur.execute(
                "INSERT INTO dealer (Dealer_ID,Name, Phone_Number, Aadhar_Number) VALUES (%s,%s, %s, %s)",
                [dealer_id,name, phone_no, aadhar_no]
            )
            
            # Commit to DB
            mysql.connection.commit()
            
            # Close cursor
            cur.close()
            
            flash(f"Account created successfully! Your User ID is {dealer_id}. You can now log in.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash(f"Database error: {e}", "danger")
            return redirect(url_for("create_account"))

    return render_template("createAccount.html")
# Home Route
@app.route('/home/')
def home():
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        return redirect(url_for('login'))

    if role in ['Admin','FCI Official']:
        return redirect(url_for('admin.homepage', id=user_id))
    elif role == "Manager":
        return redirect(url_for('employee.dashboard'))
    else:
        return redirect(url_for('dealer.dashboard'))

if __name__ == "__main__":
    app.run()
