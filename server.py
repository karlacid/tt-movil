
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "petotech1.db")

def crear_base_datos():
    """Crea la base de datos y las tablas si no existen."""
    print(f"🔹 Creando base de datos en: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contrasena TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS puntajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            color TEXT NOT NULL,
            puntos INTEGER DEFAULT 0
        )
    """)

    # Aseguramos que haya filas base para azul y rojo
    for color in ["azul", "rojo"]:
        cursor.execute("INSERT OR IGNORE INTO puntajes (color, puntos) VALUES (?, 0)", (color,))

    # Creamos una contraseña de ejemplo si no hay usuarios
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios (contrasena) VALUES (?)", ("123",))

    conn.commit()
    conn.close()
    print("Base de datos creada o ya existente")

def obtener_puntaje(color):
    """Obtiene los puntos actuales del color."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT puntos FROM puntajes WHERE color = ?", (color,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def actualizar_puntaje(color, puntos_a_sumar):
    """Suma puntos al color indicado."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE puntajes SET puntos = puntos + ? WHERE color = ?", (puntos_a_sumar, color))
    conn.commit()
    conn.close()



@app.route("/login", methods=["POST"])
def login():
    """Verifica si la contraseña existe en la base de datos."""
    data = request.get_json()
    password = data.get("password")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE contrasena = ?", (password,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"status": "ok", "message": "Acceso concedido"})
    else:
        return jsonify({"status": "error", "message": "Contraseña incorrecta"}), 401

@app.route("/crear_usuario", methods=["POST"])
def crear_usuario():
    """Permite agregar una nueva contraseña al sistema."""
    data = request.get_json()
    nueva_contrasena = data.get("password")

    if not nueva_contrasena:
        return jsonify({"status": "error", "message": "No se proporcionó una contraseña"}), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (contrasena) VALUES (?)", (nueva_contrasena,))
        conn.commit()
        conn.close()
        print(f"Nueva contraseña agregada: {nueva_contrasena}")
        return jsonify({"status": "ok", "message": "Usuario creado correctamente"})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "La contraseña ya existe"}), 409

@app.route("/registrar_puntos", methods=["POST"])
def registrar_puntos():
    """Registra puntos en la base de datos."""
    data = request.get_json()
    color = data.get("color")
    puntos_a_sumar = int(data.get("puntos", 0))

    if color not in ["azul", "rojo"]:
        return jsonify({"status": "error", "message": "Color inválido"}), 400

    actualizar_puntaje(color, puntos_a_sumar)
    nuevo_total = obtener_puntaje(color)

    print(f"{color.upper()} +{puntos_a_sumar} → Total: {nuevo_total}")
    return jsonify({"status": "ok", "puntos": nuevo_total})

@app.route("/alerta", methods=["POST"])
def alerta():
    """Registra un evento de alerta."""
    data = request.get_json()
    mensaje = data.get("mensaje", "Alerta sin mensaje")
    print(f"⚠️ ALERTA RECIBIDA: {mensaje}")
    return jsonify({"status": "ok", "message": "Alerta registrada"})

@app.route("/puntos", methods=["GET"])
def puntos():
    """Devuelve los puntos actuales de azul y rojo."""
    azul = obtener_puntaje("azul")
    rojo = obtener_puntaje("rojo")
    return jsonify({"azul": azul, "rojo": rojo})


if __name__ == "__main__":
    crear_base_datos()
    print("=== SERVIDOR PETOTECH INICIADO ===")
    print(f"Base de datos: {DB_PATH}")
    print("Rutas activas: /login, /crear_usuario, /registrar_puntos, /alerta, /puntos")
    print("===================================")
    app.run(host="0.0.0.0", port=5000)
