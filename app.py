import os
import sqlite3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_NAME = "./database/data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            card_price REAL,
            about TEXT,
            image_path TEXT
        )
    """)
    conn.commit()
    conn.close()

@app.route("/api/products", methods=["POST"])
def add_product():
    name = request.form.get("name")
    price = request.form.get("price")
    card_price = request.form.get("card_price")
    about = request.form.get("about")
    file = request.files.get("image")

    image_url = None
    if file:
        filename = file.filename
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(image_path)
        image_url = request.host_url + "uploads/" + filename   # ✅ avtomatik URL

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO products (name, price, card_price, about, image_path) VALUES (?, ?, ?, ?, ?)",
        (name, price, card_price, about, image_url)
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

@app.route("/api/products", methods=["GET"])
def get_products():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    rows = c.fetchall()
    data = [dict(row) for row in rows]
    conn.close()
    return jsonify(data)

# 📌 uploads papkasidan rasm olish uchun
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
