from flask import Flask, render_template, redirect, request, jsonify, url_for
import sqlite3
import json
import uuid

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_ref TEXT,
            table_no TEXT,
            customer_name TEXT,
            phone TEXT,
            items TEXT,
            subtotal REAL,
            tax REAL,
            total REAL,
            status TEXT DEFAULT 'Confirmed',
            payment_status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            res_ref TEXT,
            guest_name TEXT,
            phone TEXT,
            date TEXT,
            slot TEXT,
            people INTEGER,
            note TEXT,
            table_no TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # NEW: delivery_orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS delivery_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_ref TEXT,
            customer_name TEXT,
            phone TEXT,
            address TEXT,
            city TEXT,
            pincode TEXT,
            notes TEXT,
            items TEXT,
            subtotal REAL,
            delivery_fee REAL DEFAULT 40,
            gst REAL,
            total REAL,
            status TEXT DEFAULT 'Confirmed',
            payment_status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def init_customers_db():
    conn = sqlite3.connect("asma.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dodo(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()
init_customers_db()

@app.route("/")
def frontpage():
    return render_template("home.html")

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/registration")
def registration():
    return render_template("registration.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/menu")
def menu():
    return render_template("menu.html")

@app.route("/main course")
def maincourse():
    return render_template("main course.html")

@app.route("/starter")
def starter():
    return render_template("starter.html")

@app.route("/desert")
def desert():
    return render_template("desert.html")

@app.route("/Location")
def Location():
    return render_template("Location.html")

@app.route("/language")
def Language():
    return render_template("language.html")

@app.route("/Availability")
def Availability():
    return render_template("Availability.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/Table reservation")
def Table():
    return render_template("Table reservation.html")

@app.route("/About")
def About():
    return render_template("About.html")

@app.route("/User profile")
def User():
    return render_template("User profile.html")

@app.route("/Billing")
def Billing():
    return render_template("delivery.html")

@app.route("/Rating and Review")
def review():
    return render_template("Rating and Review.html")

@app.route("/Employee")
def employee():
    return render_template("Employee.html")

@app.route("/new_order")
def new_order():
    return render_template("new_order.html")

@app.route("/delivery")
def delivery_page():
    return render_template("home_delivery.html")

@app.route('/submit', methods=["POST"])
def submit():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    address = request.form.get("address")
    conn = sqlite3.connect("asma.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO dodo(name, email, phone, address) VALUES (?, ?, ?, ?)", (name, email, phone, address))
    conn.commit()
    conn.close()
    return redirect(url_for('menu'))

@app.route("/order")
def order_page():
    return render_template("orders.html")

# ── TABLE ORDERS ──────────────────────────────────────────────────────────────
@app.route("/api/orders", methods=["GET"])
def api_orders():
    conn = sqlite3.connect("orders.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    orders = []
    for r in rows:
        orders.append({
            "id": r["id"],
            "order_ref": r["order_ref"] or f"DI-{r['id']:03d}",
            "table_no": r["table_no"],
            "customer_name": r["customer_name"],
            "phone": r["phone"],
            "items": json.loads(r["items"]) if r["items"] else [],
            "subtotal": r["subtotal"],
            "tax": r["tax"],
            "total": r["total"],
            "status": r["status"] or "Confirmed",
            "payment_status": r["payment_status"] or "Pending",
            "created_at": r["created_at"],
            "type": "table"
        })
    return jsonify(orders)

@app.route("/save_order", methods=["POST"])
def save_order():
    data = request.json
    order_ref = "DI-" + str(uuid.uuid4())[:6].upper()
    table_no = data.get("table_no", "")
    customer_name = data.get("customer_name", "")
    phone = data.get("phone", "")
    items = json.dumps(data.get("items", []))
    subtotal = data.get("subtotal", 0)
    tax = data.get("tax", 0)
    total = data.get("total", 0)
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO orders (order_ref, table_no, customer_name, phone, items, subtotal, tax, total, status, payment_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Confirmed', 'Pending')
    """, (order_ref, table_no, customer_name, phone, items, subtotal, tax, total))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"status": "success", "order_ref": order_ref, "order_id": new_id})

@app.route("/api/order/<int:order_id>/status", methods=["POST"])
def update_order_status(order_id):
    data = request.json
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status=? WHERE id=?", (data.get("status"), order_id))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/api/order/<int:order_id>/payment", methods=["POST"])
def update_payment_status(order_id):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET payment_status='Paid' WHERE id=?", (order_id,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

# ── RESERVATIONS ──────────────────────────────────────────────────────────────
@app.route("/api/reservations", methods=["GET"])
def api_reservations():
    conn = sqlite3.connect("orders.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reservations ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "res_ref": r["res_ref"] or f"RES-{r['id']:03d}",
            "guest_name": r["guest_name"],
            "phone": r["phone"],
            "date": r["date"],
            "slot": r["slot"],
            "people": r["people"],
            "note": r["note"],
            "table_no": r["table_no"],
            "status": r["status"],
            "created_at": r["created_at"],
        })
    return jsonify(result)

@app.route("/api/reservations", methods=["POST"])
def save_reservation():
    data = request.json
    res_ref = "RES-" + str(uuid.uuid4())[:6].upper()
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reservations (res_ref, guest_name, phone, date, slot, people, note, table_no, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pending')
    """, (res_ref, data.get("guest_name",""), data.get("phone",""), data.get("date",""),
          data.get("slot",""), data.get("people",1), data.get("note",""), data.get("table_no","")))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "res_ref": res_ref})

@app.route("/api/reservations/<int:res_id>/status", methods=["POST"])
def update_reservation_status(res_id):
    data = request.json
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE reservations SET status=? WHERE id=?", (data.get("status"), res_id))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

# ── DELIVERY ORDERS ───────────────────────────────────────────────────────────
@app.route("/api/delivery_orders", methods=["GET"])
def api_delivery_orders():
    conn = sqlite3.connect("orders.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM delivery_orders ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            "id": r["id"],
            "order_ref": r["order_ref"] or f"DEL-{r['id']:03d}",
            "customer_name": r["customer_name"],
            "phone": r["phone"],
            "address": r["address"],
            "city": r["city"],
            "pincode": r["pincode"],
            "notes": r["notes"],
            "items": json.loads(r["items"]) if r["items"] else [],
            "subtotal": r["subtotal"],
            "delivery_fee": r["delivery_fee"],
            "gst": r["gst"],
            "total": r["total"],
            "status": r["status"] or "Confirmed",
            "payment_status": r["payment_status"] or "Pending",
            "created_at": r["created_at"],
            "type": "delivery"
        })
    return jsonify(result)

@app.route("/api/delivery_orders", methods=["POST"])
def save_delivery_order():
    data = request.json
    order_ref = "DEL-" + str(uuid.uuid4())[:6].upper()
    items_raw = data.get("items", [])
    # Normalize items: support both {name,qty,price} and plain strings
    items_list = []
    for it in items_raw:
        if isinstance(it, dict):
            items_list.append(it)
        else:
            items_list.append({"name": str(it), "qty": 1, "price": 0})
    items_json = json.dumps(items_list)
    subtotal = data.get("subtotal", 0)
    gst = data.get("gst", 0)
    delivery_fee = data.get("delivery_fee", 40)
    total = data.get("total", 0)
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO delivery_orders
            (order_ref, customer_name, phone, address, city, pincode, notes, items,
             subtotal, delivery_fee, gst, total, status, payment_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Confirmed', 'Pending')
    """, (
        order_ref,
        data.get("customer_name", ""),
        data.get("phone", ""),
        data.get("address", ""),
        data.get("city", ""),
        data.get("pincode", ""),
        data.get("notes", ""),
        items_json,
        subtotal, delivery_fee, gst, total
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"status": "success", "order_ref": order_ref, "order_id": new_id})

@app.route("/api/delivery_orders/<int:order_id>/status", methods=["POST"])
def update_delivery_status(order_id):
    data = request.json
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE delivery_orders SET status=? WHERE id=?", (data.get("status"), order_id))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/api/delivery_orders/<int:order_id>/payment", methods=["POST"])
def update_delivery_payment(order_id):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE delivery_orders SET payment_status='Paid' WHERE id=?", (order_id,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)