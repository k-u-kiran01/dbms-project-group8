from flask import Flask,Blueprint,request,redirect,url_for,session,render_template,flash
from flask_mysqldb import MySQL
from datetime import date
from MySQLdb.cursors import DictCursor

admin = Blueprint('admin', __name__, url_prefix='/admin', 
                  template_folder='templatesadm', static_folder='static')

def getLastMonthProc():
    from app import mysql
    cursor=mysql.connection.cursor()
    cursor.execute("""
    SELECT count(P_ID) FROM procurement
    where month(current_date()) - month(Date)=1;
    """)
    proc=cursor.fetchone()
    print(proc)
    return proc['count(P_ID)']
def activeUsers():
    from app import mysql
    cursor=mysql.connection.cursor()
    cursor.execute("""
    SELECT count(User_ID) FROM users
    where Role = 'Dealer' or Role = 'Manager';
    """)
    users=cursor.fetchone()
    return users['count(User_ID)']
def delLastMonth():
    from app import mysql
    cursor=mysql.connection.cursor()
    cursor.execute("""
    SELECT count(Delivery_ID) FROM delivery
where month(current_date()) - month(Delivery_Date);
    """)
    deliveries=cursor.fetchone()
    return deliveries['count(Delivery_ID)']
def totalpendGrievances():
    from app import mysql
    cursor=mysql.connection.cursor()
    cursor.execute("""
    SELECT count(Grievance_ID) FROM grievance
    where  Status = 'Open';
    """)
    grv=cursor.fetchone()
    return grv['count(Grievance_ID)']

@admin.route('/homepage',methods=['GET','POST'])

def homepage():
    return render_template("index.html",role=session['role'],plm=getLastMonthProc(),dlm=delLastMonth(),au=activeUsers(),pg=totalpendGrievances())

@admin.route('/dealers',methods=['GET'])
def dealerList():
    if 'user_id' not in session or (session['role'] != "Admin" and session['role'] !="FCI OFFICIAL"):
        redirect(url_for('login'))
    try:
        search_id = request.args.get("search_id")
        from app import mysql
        cursor=mysql.connection.cursor(DictCursor)
        if search_id:
            cursor.execute("""
            SELECT * FROM dealer WHERE Dealer_ID=%s;
            """,(search_id,))
        else:
            cursor.execute("""
            SELECT * FROM dealer
            """)
        dealer_data=cursor.fetchall()
    #print(dealer_data)
        cursor.close()
        return render_template("dealers.html",role=session['role'],dealers=dealer_data)
    except Exception as e:
        print(f"Error fetching Dealers data: {e}")
        flash("An error occurred while loading Dealers data.", "danger")
        return redirect(url_for("admin.homepage"))

@admin.route('/grievances',methods=['GET'])
def allgrievances():
    if 'user_id' not in session or (session['role'] != "Admin" and session['role'] !="FCI OFFICIAL"):
        redirect(url_for('login'))
    search_id=request.args.get('search_id')
    from app import mysql
    cursor=mysql.connection.cursor()
    if search_id:
        cursor.execute("SELECT * FROM grievance WHERE Grievance_ID=%s;",(search_id,))
    else:
        cursor.execute("SELECT * FROM grievance;")
    grievance_data=cursor.fetchall()
    cursor.close()
    return render_template("allgrievances.html",role=session['role'],grievances=grievance_data)

@admin.route("/edit_grievance_status/<int:grievance_id>", methods=["POST"])
def edit_grievance_status(grievance_id):
    # Check if user is logged in and has the correct role
    if "user_id" not in session or (session['role'] != "Admin" and session['role'] !="FCI OFFICIAL"):
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
    
    return redirect(url_for("admin.allgrievances"))
@admin.route('/procurements',methods=['GET'])
def allProcurements():
    if 'user_id' not in session or (session['role'] != "Admin" and session['role'] !="FCI OFFICIAL"):
        redirect(url_for('login'))
    from app import mysql
    cursor=mysql.connection.cursor()
    search_id=request.args.get('search_id')
    select_id=request.args.get('select_id')
    if search_id:
        cursor.execute("""
        select P_ID, Grain_Quantity, Price, Date, p.Inventory_ID, i.Warehouse_ID,Dealer_ID, Grain_Type from 
        procurement  p inner join inventory i 
        on p.Inventory_ID=i.Inventory_ID 
        join grains g 
        on p.Grain_ID=g.Grain_ID
        where p.P_ID=%s;
        """,(search_id,))

    elif select_id:
        cursor.execute("""
        select P_ID, Grain_Quantity, Price, Date, p.Inventory_ID, i.Warehouse_ID,Dealer_ID, Grain_Type from 
        procurement  p inner join inventory i 
        on p.Inventory_ID=i.Inventory_ID 
        join grains g 
        on p.Grain_ID=g.Grain_ID
        where i.Warehouse_ID=%s;
    """,(select_id,))
    else:
        cursor.execute("""
        select P_ID, Grain_Quantity, Price, Date, p.Inventory_ID,i.Warehouse_ID, Dealer_ID, Grain_Type from 
        procurement  p inner join inventory i 
        on p.Inventory_ID=i.Inventory_ID 
        join grains g 
        on p.Grain_ID=g.Grain_ID
    """)
    procurement_data=cursor.fetchall()
    cursor.execute("SELECT Warehouse_ID,Location FROM warehouse;")
    
    warehouses=cursor.fetchall()
    #print(warehouses)
    cursor.close()
    return render_template('allprocurements.html',role=session['role'],warehouses=warehouses,procurements=procurement_data)

# @admin.route('/warehouses', methods=['GET'])
# def allwarehouses():
#     from app import mysql
#     if 'user_id' not in session or session['role'] != "Dealer":
#         return redirect(url_for('login'))  # Fixed missing return statement

#     cursor = mysql.connection.cursor(DictCursor)

#     search_id = request.args.get('search_id')
    
#     if search_id:
#         cursor.execute("""
#             SELECT Inventory_ID,Stock,Grain_Type, Capacity,Warehouse_ID FROM inventory 
#             INNER JOIN grains on grains.Grain_ID=inventory.Grain_ID
#             WHERE Warehouse_ID = %s
#         """, (search_id,))
#         inventory_data = cursor.fetchall()
#     else:
#         cursor.execute("""
#             select sum(Stock),sum(capacity)
#             from inventory 
#             where Warehouse_ID=%s;
#         """,(search_id,))
#         warehouse_data = cursor.fetchall()
#         cursor.execute(select )
    
#     cursor.close()

#     return render_template('warehouses.html', inventories=inventory_data if search_id else [], warehouses=warehouse_data if not search_id else [])
@admin.route('/warehouses', methods=['GET'])
def allwarehouses():
    from app import mysql
    if 'user_id' not in session or (session['role'] not in ['Admin','FCI Official']):
        return redirect(url_for('login'))
        
    cursor = mysql.connection.cursor(DictCursor)
    select_id = request.args.get('select_id')  # Changed from search_id
    
    if select_id:
        cursor.execute("""
            SELECT Inventory_ID, Stock, Grain_Type, Capacity, Warehouse_ID
            FROM inventory
            INNER JOIN grains ON grains.Grain_ID = inventory.Grain_ID
            WHERE Warehouse_ID = %s
        """, (select_id,))  # Changed from search_id
        inventory_data = cursor.fetchall()
        warehouse_data = []
    else:
        # Your existing warehouse query
        cursor.execute("""
            SELECT w.Warehouse_ID, w.Location, COALESCE(SUM(i.Stock), 0) AS Total_Stock,
                   COALESCE(SUM(i.Capacity), 0) AS Total_Capacity
            FROM warehouse w
            LEFT JOIN inventory i ON w.Warehouse_ID = i.Warehouse_ID
            GROUP BY w.Warehouse_ID, w.Location
        """)
        warehouse_data = cursor.fetchall()
        inventory_data = []
        
    cursor.close()
    return render_template('warehouses.html', 
                           role=session['role'],
                          inventories=inventory_data, 
                          warehouses=warehouse_data,
                          select_id=select_id)  # Pass select_id to the template
# @admin.route('/users',methods=['GET'])
# def users():
#     if 'user_id' not in session or (session['role'] != "Admin" and session['role'] !="FCI OFFICIAL"):
#         redirect(url_for('login'))
#     from app import mysql
#     cursor=mysql.connection.cursor(DictCursor)
#     cursor.execute("SELECT * FROM users WHERE Role <> %s AND Role <> %s",('FCI OFFICIAL','Admin',))
#     user_data=cursor.fetchall()
#     #print(user_data)
#     cursor.close()
#     return render_template('users.html',role=session['role'],users=user_data)
@admin.route('/users', methods=['GET'])
def users():
    from app import mysql
    if 'user_id' not in session or (session['role'] != "Admin" and session['role'] != "FCI OFFICIAL"):
        return redirect(url_for('login'))

    search_id = request.args.get('search_id')

    cursor = mysql.connection.cursor()
    if search_id:
        # If searching, get that specific user
        cursor.execute("SELECT * FROM users WHERE User_ID = %s", [search_id])
    else:
        # Otherwise get all non-admin users
        cursor.execute("SELECT * FROM users WHERE Role <> %s AND Role <> %s", ('FCI OFFICIAL', 'Admin'))
    
    user_data = cursor.fetchall()
    cursor.close()

    return render_template('users.html', role=session['role'], users=user_data)

@admin.route('/removeUser',methods=['POST'])
def remove_user():
    from app import mysql
    cursor=mysql.connection.cursor(DictCursor)
    user_id=request.form.get('user_id')
    cursor.execute("""
    DELETE FROM users WHERE User_ID=%s
    """,(user_id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('admin.users'))
@admin.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))
