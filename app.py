import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "tu_clave_secreta_aqui"  # CAMBIAR en producción

DB = "macros.db"

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# Decorador para rutas que requieren login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validaciones
        if not username:
            return render_template("register.html", error="Debe ingresar un usuario")
        if not password:
            return render_template("register.html", error="Debe ingresar una contraseña")
        if password != confirmation:
            return render_template("register.html", error="Las contraseñas no coinciden")

        # Verificar si el usuario ya existe
        db = get_db()
        existing = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if existing:
            return render_template("register.html", error="El usuario ya existe")

        # Crear usuario
        hash_password = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            (username, hash_password)
        )
        db.commit()

        # Iniciar sesión automáticamente
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        session["user_id"] = user["id"]
        session["username"] = user["username"]

        return redirect("/")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Limpiar sesión
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return render_template("login.html", error="Debe ingresar un usuario")
        if not password:
            return render_template("login.html", error="Debe ingresar una contraseña")

        # Verificar credenciales
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user is None or not check_password_hash(user["hash"], password):
            return render_template("login.html", error="Usuario o contraseña incorrectos")

        # Iniciar sesión
        session["user_id"] = user["id"]
        session["username"] = user["username"]

        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/")
@login_required
def index():
    db = get_db()
    user_id = session["user_id"]
    
    goal = db.execute(
        "SELECT * FROM goals WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (user_id,)
    ).fetchone()

    # Obtener totales del día
    today_totals = db.execute(
        """
        SELECT 
            COALESCE(SUM(protein_g), 0) as protein,
            COALESCE(SUM(carbs_g), 0) as carbs,
            COALESCE(SUM(fat_g), 0) as fat,
            COALESCE(SUM(calories), 0) as calories
        FROM meals
        WHERE user_id = ? AND DATE(created_at) = DATE('now')
        """,
        (user_id,)
    ).fetchone()

    # Obtener peso actual
    current_weight = db.execute(
        "SELECT weight_kg FROM weight WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (user_id,)
    ).fetchone()

    return render_template(
        "index.html",
        goal=goal,
        today=today_totals,
        weight=current_weight
    )


@app.route("/goals", methods=["GET", "POST"])
@login_required
def goals():
    db = get_db()
    user_id = session["user_id"]

    if request.method == "POST":
        protein = int(request.form.get("protein_g", 0))
        carbs = int(request.form.get("carbs_g", 0))
        fat = int(request.form.get("fat_g", 0))
        calories = request.form.get("calories", "")

        # Validar
        if protein < 0 or carbs < 0 or fat < 0:
            return redirect("/goals")

        # Calcular calorías si no se ingresó
        if not calories:
            calories = None
        else:
            calories = int(calories)

        db.execute(
            """
            INSERT INTO goals (user_id, protein_g, carbs_g, fat_g, calories)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, protein, carbs, fat, calories)
        )
        db.commit()
        return redirect("/")

    # GET
    goal = db.execute(
        "SELECT * FROM goals WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (user_id,)
    ).fetchone()

    return render_template("goals.html", goal=goal)


@app.route("/meals", methods=["GET", "POST"])
@login_required
def meals():
    db = get_db()
    user_id = session["user_id"]

    if request.method == "POST":
        food_id = int(request.form.get("food_id"))
        grams = float(request.form.get("grams"))

        food = db.execute(
            "SELECT * FROM foods WHERE id = ?",
            (food_id,)
        ).fetchone()
        
        protein = food["protein_100g"] * grams / 100
        carbs = food["carbs_100g"] * grams / 100
        fat = food["fat_100g"] * grams / 100
        calories = protein * 4 + carbs * 4 + fat * 9
        
        db.execute(
            """
            INSERT INTO meals (user_id, food_id, grams, protein_g, carbs_g, fat_g, calories)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, food_id, grams, protein, carbs, fat, calories)
        )
        db.commit()
        return redirect("/meals")

    # GET
    foods = db.execute("SELECT * FROM foods ORDER BY name")
    
    meals_list = db.execute(
        """
        SELECT meals.*, foods.name
        FROM meals
        JOIN foods ON meals.food_id = foods.id
        WHERE meals.user_id = ? AND DATE(meals.created_at) = DATE('now')
        ORDER BY meals.created_at DESC
        """,
        (user_id,)
    )
    
    return render_template("meals.html", foods=foods, meals=meals_list)



if __name__ == "__main__":
    app.run(debug=True)