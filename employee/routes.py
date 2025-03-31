from flask import Blueprint, request, redirect, url_for, session, render_template, flash,jsonify
from datetime import date
from flask_mysqldb import MySQL
import os
from MySQLdb.cursors import DictCursor
from MySQLdb import Error

# Correct the template folder path
employee = Blueprint(
    'employee',
    __name__,
    url_prefix='/employee',
    template_folder='templatesemp',
    static_folder='static'
)

def get_manager_warehouse():
    if "user_id" not in session:
        return None
    
    from app import mysql
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute("SELECT Warehouse_Number FROM employee WHERE Manager_ID=%s;", (session["user_id"],))
    warehouse_data = cursor.fetchone()
    cursor.close()
    return warehouse_data['Warehouse_Number'] if warehouse_data else None


# Fetch Stock Summary
def fetch_stock_summary(mysql):
    try:
        cursor = mysql.connection.cursor(DictCursor)
        # Fetch total stock
        cursor.execute("SELECT COALESCE(SUM(Inventory_Count), 0) AS total_stock FROM warehouse")
        total_stock = cursor.fetchone()["total_stock"]

        # Fetch total capacity
        cursor.execute("SELECT COALESCE(SUM(Capacity), 0) AS total_capacity FROM warehouse")
        total_capacity = cursor.fetchone()["total_capacity"]

        return int(total_stock), int(total_capacity)
    except Exception as e:
        print(f"Error fetching stock summary: {e}")
        return 0, 0
    finally:
        if 'cursor' in locals():
            cursor.close()

# Fetch Pending Grievances
def fetch_pending_grievances(mysql):
    try:
        cursor = mysql.connection.cursor(DictCursor)
        # Count grievances with status "Pending"
        cursor.execute("SELECT COUNT(*) AS pending_count FROM grievance WHERE Status='Open'")
        pending_grievances = cursor.fetchone()["pending_count"]
        return pending_grievances
    except Exception as e:
        print(f"Error fetching pending grievances: {e}")
        return 0
    finally:
        if 'cursor' in locals():
            cursor.close()

# Dashboard Route
@employee.route("/dashboard", methods=["GET"])
def dashboard():
    # Check if user is logged in and has the correct role
    if "user_id" not in session:
        flash("Please log in to access the dashboard.", "danger")
        return redirect(url_for("login"))

    if session.get('role') not in ['Manager', 'Admin']:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))

    try:
        from app import mysql  # Import mysql dynamically to avoid circular import

        # Fetch stock summary and pending grievances
        total_stock, total_capacity = fetch_stock_summary(mysql)
        pending_grievances = fetch_pending_grievances(mysql)

        # Render dashboard template with variables
        return render_template(
            "dashboard.html",
            role=session['role'],
            total_stock=total_stock,
            total_capacity=total_capacity,
            pending_grievances=pending_grievances
        )
    except Exception as e:
        print(f"Error rendering dashboard: {e}")
        flash("An error occurred while loading the dashboard.", "danger")
        return redirect(url_for("login"))

# Grievances Route
@employee.route("/grievance", methods=["GET", "POST"])
def grievance():
    # Check if user is logged in and has the correct role
    
    try:
        from app import mysql
        cursor = mysql.connection.cursor(DictCursor)

        search_id = request.args.get("search_id")
        if search_id:
            cursor.execute("SELECT Grievance_ID, Dealer_ID, Description, Status FROM grievance WHERE Grievance_ID=%s", (search_id,))
        else:
            cursor.execute("SELECT Grievance_ID, Dealer_ID, Description, Status FROM grievance")
        
        grievances_data = cursor.fetchall()
        cursor.close()
        
        return render_template("grievance.html", grievances=grievances_data, role=session['role'])
    except Exception as e:
        print(f"Error fetching grievances: {e}")
        flash("An error occurred while loading grievances.", "danger")
        return redirect(url_for("employee.dashboard"))

# Edit Grievance Status Route
@employee.route("/edit_grievance_status/<int:grievance_id>", methods=["POST"])
def edit_grievance_status(grievance_id):
    # Check if user is logged in and has the correct role
    if "user_id" not in session:
        flash("Please log in to edit grievance status.", "danger")
        return redirect(url_for("login"))
    
    if session.get('role') not in ['Manager', 'Admin']:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))
    
    try:
        from app import mysql
        cursor = mysql.connection.cursor(DictCursor)
        new_status = request.form.get("new_status")
        
        cursor.execute("UPDATE grievance SET Status=%s WHERE Grievance_ID=%s", (new_status, grievance_id))
        mysql.connection.commit()
        cursor.close()

        flash("Grievance status updated successfully!", "success")
    except Exception as e:
        print(f"Error updating grievance status: {e}")
        flash("An error occurred while updating the grievance status.", "danger")
    
    return redirect(url_for("employee.grievance"))

@employee.route("/warehouse_stock", methods=["GET"])
def warehouse_stock():
    from app import mysql
    if "user_id" not in session:
        return redirect(url_for("login"))

    warehouse_inventory_data = []
    warehouse_summary = {
        "Warehouse_ID": "",
        "Location": "",
        "Total_Stock": 0,
        "Total_Capacity": 0
    }

    try:
        cursor = mysql.connection.cursor(DictCursor)

        # Fetch manager's warehouse number
        cursor.execute("SELECT Warehouse_Number FROM employee WHERE Manager_ID = %s", (session["user_id"],))
        manager_data = cursor.fetchone()
        if not manager_data or not manager_data["Warehouse_Number"]:
            flash("No warehouse assigned to this manager.", "warning")
            return render_template("warehouse_stock.html", warehouses=warehouse_inventory_data)

        warehouse_id = manager_data['Warehouse_Number']
        search_id = request.args.get('search_id')

        # Query inventory details
        query = """
            SELECT
                i.Inventory_ID,
                g.Grain_Type AS Grain_Name,
                i.Stock AS stock,
                i.Capacity AS Capacity
            FROM inventory i
            LEFT JOIN grains g ON i.Grain_ID = g.Grain_ID
            WHERE i.Warehouse_ID = %s
        """

        params = [warehouse_id]
        if search_id:
            query += " AND i.Inventory_ID = %s"
            params.append(search_id)

        cursor.execute(query, params)
        warehouse_inventory_data = cursor.fetchall()

        # Fetch warehouse ID, location, total stock, and total capacity
        cursor.execute("""
            SELECT 
                w.Warehouse_ID, 
                w.Location, 
                SUM(i.Stock) AS Total_Stock, 
                SUM(i.Capacity) AS Total_Capacity
            FROM warehouse w
            LEFT JOIN inventory i ON w.Warehouse_ID = i.Warehouse_ID
            WHERE w.Warehouse_ID = %s
        """, (warehouse_id,))
        warehouse_summary_data = cursor.fetchone()

        if warehouse_summary_data:
            warehouse_summary = {
                "Warehouse_ID": warehouse_summary_data["Warehouse_ID"] or "N/A",
                "Location": warehouse_summary_data["Location"] or "Unknown",
                "Total_Stock": warehouse_summary_data["Total_Stock"] or 0,
                "Total_Capacity": warehouse_summary_data["Total_Capacity"] or 0
            }

    except Error as err:
        flash(f"Database Error: {err}", "danger")

    finally:
        if cursor:
            cursor.close()

    return render_template(
        "warehouse_stock.html",
        role=session.get('role', ''),
        warehouses=warehouse_inventory_data,
        warehouse_summary=warehouse_summary
    )


# Procurement Route
@employee.route("/get_dealer_info/<int:dealer_id>")
def get_dealer_info(dealer_id):
    from app import mysql
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute("SELECT Dealer_ID, Name FROM dealer WHERE Dealer_ID = %s", (dealer_id,))
    dealer = cursor.fetchone()
    cursor.close()
    return jsonify(dealer) if dealer else jsonify({"error": "Dealer not found"}), 404
@employee.route("/procurement", methods=["GET", "POST"])
def procurement():
    from app import mysql
    cursor = mysql.connection.cursor(DictCursor)

    # Get warehouse ID for current manager
    cursor.execute("SELECT Warehouse_Number FROM employee WHERE Manager_ID=%s", (session['user_id'],))
    warehouse = cursor.fetchone()
    
    if not warehouse:
        flash("Warehouse not found for the current manager.", "danger")
        return redirect(url_for("employee.dashboard"))
    
    warehouse_id = warehouse["Warehouse_Number"]
    search_id = request.args.get("search_id")

    # Fetch procurement details
    if search_id:
        cursor.execute(
            """
            SELECT p.P_ID, p.Grain_ID, p.Grain_Quantity, p.Price, p.Dealer_ID, p.Date, p.Inventory_ID
            FROM procurement p 
            JOIN inventory i ON i.Inventory_ID = p.Inventory_ID
            WHERE p.P_ID = %s AND i.Warehouse_ID = %s
            """,
            (search_id, warehouse_id,)
        )
    else:
        cursor.execute(
            """
            SELECT p.P_ID, p.Grain_ID, p.Grain_Quantity, p.Price, p.Dealer_ID, p.Date, p.Inventory_ID 
            FROM procurement p 
            JOIN inventory i ON i.Inventory_ID = p.Inventory_ID
            WHERE i.Warehouse_ID = %s
            """,
            (warehouse_id,)
        )
    
    procurements_data = cursor.fetchall()

    # Fetch dropdown data
    cursor.execute("SELECT * FROM grains")
    grains = cursor.fetchall()
    cursor.execute("SELECT * FROM dealer")
    dealers = cursor.fetchall()
    cursor.execute("SELECT * FROM inventory WHERE Warehouse_ID = %s", (warehouse_id,))
    inventories = cursor.fetchall()

    if request.method == 'POST':
        grain_id = request.form.get('grain_id')
        quantity = request.form.get('quantity', type=int)
        dealer_id = request.form.get('dealer_id')

        # Ensure all required fields are provided
        if not all([grain_id, quantity, dealer_id]):
            flash("All fields are required", "danger")
            return redirect(url_for("employee.procurement"))
        
        if quantity <= 0:
            flash("Quantity must be positive", "danger")
            return redirect(url_for("employee.procurement"))

        # Fetch grain price
        cursor.execute("SELECT Price_Per_Unit FROM grains WHERE Grain_ID = %s", (grain_id,))
        grain = cursor.fetchone()
        if not grain:
            flash("Invalid grain selected", "danger")
            return redirect(url_for("employee.procurement"))
        
        price_per_unit = grain['Price_Per_Unit']
        total_price = price_per_unit * quantity

        # Validate dealer
        cursor.execute("SELECT Dealer_ID FROM dealer WHERE Dealer_ID = %s", (dealer_id,))
        dealer = cursor.fetchone()
        if not dealer:
            flash("Invalid dealer selected", "danger")
            return redirect(url_for("employee.procurement"))
        
        # Find the inventory for this grain type in this warehouse
        cursor.execute(
            "SELECT Inventory_ID, Capacity, Stock FROM inventory WHERE Grain_ID=%s AND Warehouse_ID=%s",
            (grain_id, warehouse_id,)
        )
        inventory = cursor.fetchone()
        
        if not inventory:
            flash("No inventory found for this grain type at your warehouse", "danger")
            return redirect(url_for("employee.procurement"))
        
        inventory_id = inventory['Inventory_ID']
        
        # Check if there's enough capacity
        if inventory['Stock'] + quantity > inventory['Capacity']:
            flash("Inventory capacity exceeded", "danger")
            return redirect(url_for("employee.procurement"))
        
        # Insert into procurement table
        cursor.execute(
            """
            INSERT INTO procurement (Grain_ID, Grain_Quantity, Price, Dealer_ID, Date, Inventory_ID)
            VALUES (%s, %s, %s, %s, CURDATE(), %s)
            """, (grain_id, quantity, total_price, dealer_id, inventory_id))
        
        procurement_id = cursor.lastrowid
      
        cursor.execute(
            """
            INSERT INTO transaction1 (Amount, Status, Transaction_Date, Procurement_ID)
            VALUES (%s, %s, CURDATE(), %s)
            """, (total_price, "Completed", procurement_id))

        mysql.connection.commit()
        flash("Procurement added successfully!", "success")
        return redirect(url_for("employee.procurement"))

    return render_template(
        "procurement.html",
        role=session['role'],
        procurements=procurements_data,
        grains=grains,
        dealers=dealers,
        inventories=inventories,
    )

@employee.route("/returns", methods=["GET", "POST"])
def manage_returns():
    from app import mysql
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        return_id = request.form.get("return_id")
        action = request.form.get("action")  # Accept or Reject
        if not return_id or action not in ["accept", "reject"]:
            flash("Invalid request parameters", "danger")
            return redirect(url_for("manage_returns"))
        cursor = mysql.connection.cursor(DictCursor)
        try:
            
            
            # Fetch return details with FOR UPDATE lock
            cursor.execute("""
                SELECT r.Return_Status, d.Grain_Quantity, i.Inventory_ID
                FROM return_table r
                JOIN delivery d ON r.Delivery_ID = d.Delivery_ID
                JOIN inventory i ON i.Warehouse_ID=d.Warehouse_ID
                WHERE r.Return_ID = %s
                FOR UPDATE
            """, (return_id,))
            return_data = cursor.fetchone()
            
            if not return_data:
                flash("Return not found", "danger")
                return redirect(url_for("employee.manage_returns"))
            
            if return_data['Return_Status'] != 'Pending':
                flash("This return has already been processed", "warning")
                return redirect(url_for("employee.manage_returns"))
            
            # Update return status
            new_status = "Accepted" if action == "accept" else "Rejected"
            cursor.execute("""
                UPDATE return_table
                SET Return_Status = %s,
                    Processed_By = %s,
                    Processed_Date = CURDATE()
                WHERE Return_ID = %s
            """, (new_status, session['user_id'], return_id))
            
            # If accepted, update inventory
            if action == "accept":
                cursor.execute("""
                    UPDATE inventory
                    SET Stock = Stock + %s
                    WHERE Inventory_ID = %s
                """, (return_data['Grain_Quantity'], return_data['Inventory_ID']))
                flash("Return accepted and inventory updated", "success")
            else:
                flash("Return rejected", "success")
            
            mysql.connection.commit()  # Commit the transaction
        finally:
            if cursor:
                cursor.close()
        
        return redirect(url_for("employee.manage_returns"))
    
    # GET request - show returns
    returns_data = fetch_returns()
    #print(returns_data)
    return render_template("managereturns.html", returns=returns_data, role=session["role"])

def fetch_returns():
    warehouse_id = get_manager_warehouse()
    if not warehouse_id:
        return []
    from app import mysql
    try:
        cursor = mysql.connection.cursor(DictCursor)

       
        cursor.execute("""
            SELECT 
                r.Return_ID,
                g.Grain_Type AS Product,
                d.Grain_Quantity AS Quantity,
                r.Return_Status AS Status,
                u.Name AS Processed_By,
                r.Return_Date,
                de.Name AS Customer_Name
            FROM return_table r
            JOIN delivery d ON r.Delivery_ID = d.Delivery_ID
            JOIN grains g ON d.Grain_ID = g.Grain_ID
            LEFT JOIN users u ON r.Processed_By = u.User_ID
            LEFT JOIN dealer de ON d.Dealer_ID = de.Dealer_ID
            WHERE d.Warehouse_ID = %s
            ORDER BY r.Return_ID DESC
        """, (warehouse_id,))

        returns = cursor.fetchall()
        return returns

    finally:
        if 'cursor' in locals():
            cursor.close()



def fetch_deliveries():
    warehouse_id = get_manager_warehouse()
    if not warehouse_id:
        return []
    from app import mysql
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute("""
            SELECT
                d.Delivery_ID,
                de.Name AS Customer_Name,
                de.Phone_Number AS Phone_No,
                g.Grain_Type AS Product,
                d.Grain_Quantity AS Quantity
            FROM delivery d
            JOIN grains g ON d.Grain_ID = g.Grain_ID
            LEFT JOIN dealer de ON d.Dealer_ID = de.Dealer_ID
            WHERE d.Warehouse_ID = %s
        """, (warehouse_id,))
    deliveries = cursor.fetchall()
    cursor.close()
    return deliveries
@employee.route("/deliveries")
def manage_deliveries():
    if "user_id" not in session:
        return redirect(url_for("login"))
    deliveries_data = fetch_deliveries()
    return render_template("deliveries.html", deliveries=deliveries_data, role=session["role"])


# Employees Route
@employee.route("/employees", methods=["GET", "POST"])
def employees():
    # Check if user is logged in and has the correct role
    if "user_id" not in session:
        flash("Please log in to access employees.", "danger")
        return redirect(url_for("login"))
    
    if session.get('role') not in ['Manager', 'Admin']:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))
    
    try:
        from app import mysql
        cursor = mysql.connection.cursor(DictCursor)

        search_id = request.args.get("search_id")
        if search_id:
            cursor.execute(
                """
                SELECT Manager_ID, Manager_Name
                FROM employee WHERE Employee_ID=%s""",
                (search_id,)
            )
        else:
            cursor.execute(
                """
                SELECT Manager_ID, Manager_Name
                FROM employee"""
            )

        employees_data = cursor.fetchall()
        cursor.close()
        
        return render_template(
            "employees.html",
            employees=employees_data,
            role=session.get('role')
        )
    except Exception as e:
        print(f"Error fetching employees data: {e}")
        flash("An error occurred while loading employee data.", "danger")
        return redirect(url_for("employee.dashboard"))

# Logout Route
@employee.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))
