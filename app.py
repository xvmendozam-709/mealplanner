import sqlite3

from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__)

DB = "macros.db"


def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    conn = sqlite3.connect("macros.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    conn = get_db_connection()
    goal = conn.execute(
        "SELECT protein_g, carbs_g, fat_g, calories FROM goals ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return render_template("index.html", goal=goal)


@app.route("/goals", methods=["GET", "POST"])
def goals():
    if request.method == "POST":
        protein = request.form.get("protein_g", "0")
        carbs = request.form.get("carbs_g", "0")
        fat = request.form.get("fat_g", "0")
        calories = request.form.get("calories", "")

        # Guardrails simples
        protein = int(protein) if protein else 0
        carbs = int(carbs) if carbs else 0
        fat = int(fat) if fat else 0
        calories = int(calories) if calories else None

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO goals (protein_g, carbs_g, fat_g, calories) VALUES (?, ?, ?, ?)",
            (protein, carbs, fat, calories),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    # GET
    conn = get_db_connection()
    goal = conn.execute(
        "SELECT protein_g, carbs_g, fat_g, calories FROM goals ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return render_template("goals.html", goal=goal)


@app.route("/meals", methods=["GET", "POST"])
def meals():
    db = get_db()

    # Por ahora usamos user_id=1 (luego implementaremos login)
    user_id = 1

    if request.method == "POST":
        food_id = int(request.form.get("food_id"))
        grams = float(request.form.get("grams"))

        food = db.execute(
            "SELECT * FROM foods WHERE id = ?",
            (food_id,)
        )[0]

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
    foods = db.execute("SELECT * FROM foods")

    meals = db.execute(
        """
        SELECT meals.*, foods.name
        FROM meals
        JOIN foods ON meals.food_id = foods.id
        WHERE meals.user_id = ? AND DATE(meals.created_at) = DATE('now')
        ORDER BY meals.created_at DESC
        """,
        (user_id,)
    )

    return render_template("meals.html", foods=foods, meals=meals)
