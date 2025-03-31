from flask import Flask,Blueprint,request,redirect,url_for,session,render_template,flash
#from mysql.connector import Error
from flask_mysqldb import MySQL
from datetime import date
from MySQLdb.cursors import DictCursor

template_folder='templates'

dealer = Blueprint('dealer', __name__, url_prefix='/dealer', template_folder='templates',static_folder='static')

def Procurementscount(id):
    from app import mysql
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute("SELECT count(P_ID) FROM procurement WHERE Dealer_ID=%s;",(id,))
    procurements=cursor.fetchone()
    cursor.close()
    return procurements['count(P_ID)']
def Ordercount(id):
    from app import mysql
    cursor=mysql.connection.cursor(DictCursor)
    cursor.execute("SELECT count(Delivery_ID) FROM delivery WHERE dealer_id=%s;",(id,))
    orders=cursor.fetchone()
    cursor.close()
    return orders['count(Delivery_ID)']
def PendingGrievancescount(id):
    from app import mysql
    cursor=mysql.connection.cursor(DictCursor)
    cursor.execute("SELECT count(Grievance_ID) FROM grievance WHERE dealer_id=%s AND Status='Open';",(id,))
    grivences=cursor.fetchone()
    cursor.close()
    return grivences['count(Grievance_ID)']
def Returnscount(id):
    from app import mysql
    cursor=mysql.connection.cursor(DictCursor)
    cursor.execute("select count(r.Return_ID) from return_table r,delivery de where  de.dealer_id=%s and r.Delivery_ID=de.Delivery_ID;",(id,))
    returns=cursor.fetchone()
    cursor.close()
    return returns['count(r.Return_ID)']

def newGrievance(userid, description):
    from app import mysql
    cursor = mysql.connection.cursor(DictCursor)

    try:
        print(description)
        cursor.execute("INSERT INTO grievance (Dealer_ID, Status, Date, Description) VALUES (%s, %s, CURDATE(), %s)", 
                       (userid, 'Open', description))

        mysql.connection.commit()
        grievance_id = cursor.lastrowid

    except Exception as e:
        print(f"Error inserting grievance: {e}")
        mysql.connection.rollback()  # Rollback in case of error
        grievance_id = None

    finally:
        cursor.close()

    return grievance_id

def addorder(userid,order):
    from app import mysql
    cursor = mysql.connection.cursor(DictCursor)

    try:
        # cursor.execute("SELECT Inventory_ID FROM grains WHERE Grain_ID=%s",(order['grain_id'],))
        # inventory=cursor.fetchone()
        print(order)
        cursor.execute("INSERT INTO delivery (Dealer_ID, Grain_ID, Delivery_Date, Grain_Quantity,Warehouse_ID) VALUES (%s, %s, CURDATE(), %s,%s)", 
                       (userid,order['grain_id'],order['quantity'],order['warehouse_ID'],))
        cursor.execute("SELECT Inventory_ID from inventory WHERE Warehouse_ID=%s AND Grain_ID=%s;",(order['grain_id'],order['Warehouse_ID']))
        inventory_ID=cursor.fetchone()
        cursor.execute("UPDATE inventory SET Stock =Stock -%s WHERE Inventory_ID=%s",(order['quantity'],inventory_ID['Inventory_ID']))
        mysql.connection.commit()
        order_id = cursor.lastrowid

    except Exception as e:
        print(f"Error inserting orders: {e}")
        mysql.connection.rollback()
        order_id= None

    finally:
        cursor.close()

    return order_id
def newReturn(userid,delivey_id):
    from app import mysql
    cursor=mysql.connection.cursor(DictCursor)
    cursor.execute("select i.Inventory_ID FROM delivery d INNER JOIN inventory i on i.Warehouse_ID=d.Warehouse_ID AND d.Delivery_ID=%s",(delivey_id,))
    inventory_id=cursor.fetchone()
    cursor.execute("""
    INSERT INTO return_table (Return_Date, Return_Status, Delivery_ID, Inventory_ID) 
    VALUES (CURDATE(), 'Pending', %s, %s);
    """,(delivey_id,inventory_id['Inventory_ID'],))
    mysql.connection.commit()
    return_id = cursor.lastrowid
    return return_id

@dealer.route('/dashboard',methods=['GET'])
def dashboard():
    if 'user_id' not in session or session['role']!="Dealer":
        redirect(url_for('login'))
    procurements=Procurementscount(session['user_id'])
    orders=Ordercount(session['user_id'])
    returns=Returnscount(session['user_id'])
    pendingGrivences=PendingGrievancescount(session['user_id'])
    return render_template('home.html',role="Dealer",qs1=procurements,qs2=orders,qs3=returns,qs4=pendingGrivences)

@dealer.route('/procurements',methods=['GET'])
def procurementSection():
    if 'user_id' not in session or session['role']!="Dealer":
        redirect(url_for('login'))
        
    try:
        search_id = request.args.get("search_id")
        from app import mysql
        cursor = mysql.connection.cursor(DictCursor)  # Use DictCursor

        if search_id:
            cursor.execute(
                """
                SELECT p.P_ID, g.Grain_Type, p.Grain_Quantity, p.Price, p.Date 
                FROM procurement p JOIN grains g on g.Grain_ID=p.Grain_ID AND  Dealer_ID=%s AND P_ID=%s
                """,
                (session['user_id'],search_id,)
            )
        else:
            cursor.execute(
                """
                SELECT p.P_ID, g.Grain_Type, p.Grain_Quantity, p.Price, p.Date 
                FROM procurement p JOIN grains g on g.Grain_ID=p.Grain_ID AND  Dealer_ID=%s
                """,(session['user_id'],)
            )
        
        procurements_data = cursor.fetchall()
        
        cursor.close()
        #print(procurements_data)
        return render_template(
            "procurements.html",
            role=session['role'],
            procurements=procurements_data
        )
    except Exception as e:
        print(f"Error fetching procurement data: {e}")
        flash("An error occurred while loading procurement data.", "danger")
        return redirect(url_for("dealer.dashboard"))

@dealer.route('/transactions',methods=['GET','POST'])
def transactions():
    if 'user_id' not in session or session['role']!="Dealer":
        redirect(url_for('login'))
    try:
        search_id=request.args.get('search_id')
        from app import mysql
        cursor=mysql.connection.cursor(DictCursor)

        if search_id:
            cursor.execute("SELECT Transaction_ID,Amount,Status,Transaction_Date,Procurement_ID FROM transaction1 t INNER JOIN procurement p ON t.Procurement_ID=p.P_ID WHERE p.Dealer_ID=%s AND p.Procurement_ID=%s;",((session['user_id']),search_id,))

        else:
            cursor.execute("SELECT Transaction_ID,Amount,Status,Transaction_Date,Procurement_ID FROM transaction1 t INNER JOIN procurement p ON t.Procurement_ID=p.P_ID WHERE p.Dealer_ID=%s;",(session['user_id'],))
        transasction_data=cursor.fetchall()
        cursor.close()
        #print(transasction_data)
        return render_template('transactions.html',role=session['role'],transactions=transasction_data)
    except Exception as e:
        print(f"Error fetching procurement data: {e}")
        flash("An error occurred while loading procurement data.", "danger")
        return redirect(url_for("dealer.dashboard"))
@dealer.route('/grievances',methods=['GET','POST'])
def grievanceSection():
    if 'user_id' not in session or session['role']!="Dealer":
        redirect(url_for('login'))
    
    try:
        search_id = request.args.get("search_id")
        from app import mysql
        cursor = mysql.connection.cursor(DictCursor)  # Use DictCursor

        if search_id:
            cursor.execute("SELECT Grievance_ID, Description, Status FROM grievance WHERE Grievance_ID=%s AND Dealer_ID=%s", (search_id,session['user_id'],))
        
        else:
            cursor.execute(
                "SELECT Grievance_ID, Description, Status FROM grievance WHERE Dealer_ID=%s", (session['user_id'],)
            )
        
        grievanceSection_data = cursor.fetchall()
        
        cursor.close()
        #print(grievanceSection_data)
        #print(procurements_data)
        return render_template(
            "grievances.html",
            role=session['role'],
            grievances=grievanceSection_data
        )
    except Exception as e:
        print(f"Error fetching procurement data: {e}")
        flash("An error occurred while loading procurement data.", "danger")
        return redirect(url_for("dealer.dashboard"))

@dealer.route('/addGrievence',methods=['GET','POST'])
def addGrievance():
    userid=session['user_id']
    if request.method=='GET':
        return render_template("addgrievence",userid=userid)
    if request.method=='POST':
        desciption=request.form.get("description")
        newGrievance(userid,desciption)
        return redirect(url_for("dealer.grievanceSection"))  
@dealer.route('/orders',methods=['GET','POST'])
def getOrders():
    if 'user_id' not in session or session['role']!="Dealer":
        redirect(url_for('login'))
    
    try:
        search_id = request.args.get("search_id")
        from app import mysql
        cursor = mysql.connection.cursor(DictCursor)  # Use DictCursor

        if search_id:
            cursor.execute("SELECT Delivery_ID, Delivery_Date, Grain_Type,Grain_Quantity FROM delivery INNER JOIN grains ON delivery.Grain_ID=grains.Grain_ID WHERE Delivery_ID=%s AND Dealer_ID=%s", (search_id,session['user_id'],))
        
        else:
            cursor.execute(
                "SELECT Delivery_ID, Delivery_Date, Grain_Type,Grain_Quantity FROM delivery  INNER JOIN grains ON delivery.Grain_ID=grains.Grain_ID WHERE Dealer_ID=%s", (session['user_id'],)
            )
        
        orders_data = cursor.fetchall()
        
        
        cursor.execute("SELECT * FROM grains;")
        items=cursor.fetchall()
        cursor.execute("SELECT Warehouse_ID,Location from warehouse")
        warehouses=cursor.fetchall()
        #print(warehouses)
        cursor.close()
        #print(procurements_data)
        return render_template(
            "orders.html",
            role=session['role'],
            orders=orders_data,items=items,warehouses=warehouses
        )
    except Exception as e:
        print(f"Error fetching procurement data: {e}")
        flash("An error occurred while loading procurement data.", "danger")
        return redirect(url_for("dealer.dashboard"))

@dealer.route('/addorder', methods=['POST'])
def addOrder():
    userid = session.get("user_id")
    
    # Debugging print statement
    print("Received Form Data:", request.form)
    
    newOrder = {
        "grain_id": request.form.get('grain_id'),
        "quantity": request.form.get('quantity'),
        "warehouse_ID": request.form.get('selwarehouse')
    }

    # Debugging print statement
    print("Parsed Order Data:", newOrder)

    if not newOrder["warehouse_ID"]:
        flash("Warehouse selection is required!", "danger")
        return redirect(url_for("dealer.getOrders"))

    addorder(userid, newOrder)
    return getOrders()


@dealer.route('/returns',methods=['GET','POST'])
def getReturns():
    if 'user_id' not in session or session['role']!="Dealer":
        redirect(url_for('login'))
    
    
    try:
        search_id = request.args.get("search_id")
        from app import mysql
        cursor = mysql.connection.cursor(DictCursor)  # Use DictCursor

        if search_id:
            cursor.execute("SELECT r.Return_ID, r.Return_Amount, r.Return_Date ,r.Return_Status, r.Delivery_ID,d.Grain_ID, d.Grain_Quantity FROM return_table r INNER JOIN delivery d on d.Delivery_ID=r.Delivery_ID WHERE d.Dealer_ID=%s AND r.Return_ID=%s;", (session['user_id'],search_id,))
        
        else:
            cursor.execute("SELECT r.Return_ID, r.Return_Amount, r.Return_Date ,r.Return_Status, r.Delivery_ID,d.Grain_ID,d.Grain_Quantity FROM return_table r INNER JOIN delivery d on d.Delivery_ID=r.Delivery_ID WHERE d.Dealer_ID=%s;",(session['user_id'],))
        
        returns_data = cursor.fetchall()
        cursor.execute("""
            SELECT d.Delivery_ID, g.Grain_Type, d.Grain_Quantity, d.Delivery_Date 
            FROM delivery d
            INNER JOIN grains g ON g.Grain_ID = d.Grain_ID
            LEFT JOIN return_table r ON d.Delivery_ID=r.Delivery_ID
            WHERE r.Delivery_ID IS NULL
            AND d.Dealer_ID = %s AND DATEDIFF(CURDATE(), d.Delivery_Date) < 7;
        """, (session['user_id'],))
        delivery_data=cursor.fetchall()
        cursor.close()
    #print(returns_data)
    #print(delivery_data)
        return render_template(
            "returns.html",
            role=session['role'],
            returns=returns_data,deliveries=delivery_data
        )
    except Exception as e:
        print(f"Error fetching procurement data: {e}")
        flash("An error occurred while loading procurement data.", "danger")
        return redirect(url_for("dealer.dashboard"))
    
@dealer.route('/addReturn',methods=['POST'])
def addReturn():
    delivery_id=request.form.get('delivery_id')
    newReturn(session['user_id'],delivery_id)
    return redirect(url_for("dealer.getReturns"))

@dealer.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))
