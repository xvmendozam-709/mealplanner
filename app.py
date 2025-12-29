import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # CHANGE in production

DB = "macros.db"

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# Decorator for routes requiring login
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

        # Validations
        if not username:
            return render_template("register.html", error="Must provide username")
        if not password:
            return render_template("register.html", error="Must provide password")
        if password != confirmation:
            return render_template("register.html", error="Passwords do not match")

        # Check if user already exists
        db = get_db()
        existing = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if existing:
            return render_template("register.html", error="Username already exists")

        # Create user
        hash_password = generate_password_hash(password)
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            (username, hash_password)
        )
        db.commit()

        # Auto login
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        session["user_id"] = user["id"]
        session["username"] = user["username"]

        return redirect("/")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Clear session
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return render_template("login.html", error="Must provide username")
        if not password:
            return render_template("login.html", error="Must provide password")

        # Verify credentials
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user is None:
            return render_template("login.html", error="User does not exist. Want to register?")
        
        if not check_password_hash(user["hash"], password):
            return render_template("login.html", error="Incorrect password")

        # Start session
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

    # Get today's totals
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

    # Get weekly averages (last 7 days)
    weekly_avg = db.execute(
        """
        SELECT 
            AVG(daily_protein) as avg_protein,
            AVG(daily_carbs) as avg_carbs,
            AVG(daily_fat) as avg_fat,
            AVG(daily_calories) as avg_calories
        FROM (
            SELECT 
                DATE(created_at) as day,
                SUM(protein_g) as daily_protein,
                SUM(carbs_g) as daily_carbs,
                SUM(fat_g) as daily_fat,
                SUM(calories) as daily_calories
            FROM meals
            WHERE user_id = ? 
            AND DATE(created_at) >= DATE('now', '-7 days')
            GROUP BY DATE(created_at)
        )
        """,
        (user_id,)
    ).fetchone()

    # Get current weight
    current_weight = db.execute(
        "SELECT weight_kg FROM weight WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (user_id,)
    ).fetchone()

    return render_template(
        "index.html",
        goal=goal,
        today=today_totals,
        weekly=weekly_avg,
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

        # Validate
        if protein < 0 or carbs < 0 or fat < 0:
            return redirect("/goals")

        # Calculate calories if not entered
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


@app.route("/add_food", methods=["POST"])
@login_required
def add_food():
    db = get_db()
    
    # Convert name to uppercase
    name = request.form.get("name").strip().upper()
    calories_100g = float(request.form.get("calories_100g"))
    protein_100g = float(request.form.get("protein_100g"))
    carbs_100g = float(request.form.get("carbs_100g"))
    fat_100g = float(request.form.get("fat_100g"))
    
    # Validations
    error = None
    
    if not name:
        error = "Must provide a food name"
    elif calories_100g < 0 or calories_100g > 900:
        error = "Calories must be between 0 and 900 kcal"
    elif protein_100g < 0 or protein_100g > 100:
        error = "Protein must be between 0 and 100 grams"
    elif carbs_100g < 0 or carbs_100g > 100:
        error = "Carbs must be between 0 and 100 grams"
    elif fat_100g < 0 or fat_100g > 100:
        error = "Fats must be between 0 and 100 grams"
    elif (protein_100g + carbs_100g + fat_100g) > 100:
        error = "Sum of macronutrients cannot exceed 100g"
    else:
        # Check if food already exists
        existing = db.execute(
            "SELECT * FROM foods WHERE name = ?",
            (name,)
        ).fetchone()
        
        if existing:
            error = f"Food '{name}' already exists in database"
    
    if error:
        foods = db.execute("SELECT * FROM foods ORDER BY name")
        meals_list = db.execute(
            """
            SELECT meals.*, foods.name
            FROM meals
            JOIN foods ON meals.food_id = foods.id
            WHERE meals.user_id = ? AND DATE(meals.created_at) = DATE('now')
            ORDER BY meals.created_at DESC
            """,
            (session["user_id"],)
        )
        from datetime import datetime
        return render_template(
            "meals.html", 
            foods=foods, 
            meals=meals_list, 
            error=error,
            current_date=datetime.now().date().strftime('%Y-%m-%d'),
            current_date_formatted=datetime.now().date().strftime('%A %d'),
            prev_date=(datetime.now().date() - __import__('datetime').timedelta(days=1)).strftime('%Y-%m-%d'),
            next_date=(datetime.now().date() + __import__('datetime').timedelta(days=1)).strftime('%Y-%m-%d'),
            today=datetime.now().date().strftime('%Y-%m-%d')
        )
    
    # Insert new food with calories
    db.execute(
        """
        INSERT INTO foods (name, protein_100g, carbs_100g, fat_100g, calories_100g)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, protein_100g, carbs_100g, fat_100g, calories_100g)
    )
    db.commit()
    
    # Redirect with success message
    return redirect("/meals")


@app.route("/meals", methods=["GET", "POST"])
@login_required
def meals():
    from datetime import datetime, timedelta
    
    db = get_db()
    user_id = session["user_id"]
    
    # Get date parameter (default to today)
    date_param = request.args.get('date')
    if date_param:
        try:
            current_date = datetime.strptime(date_param, '%Y-%m-%d').date()
        except:
            current_date = datetime.now().date()
    else:
        current_date = datetime.now().date()
    
    today = datetime.now().date()
    
    # Calculate previous and next dates
    prev_date = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')
    next_date = (current_date + timedelta(days=1)).strftime('%Y-%m-%d')
    current_date_str = current_date.strftime('%Y-%m-%d')
    
    # Format date for display (e.g., "Sunday 28")
    current_date_formatted = current_date.strftime('%A %d')

    if request.method == "POST":
        food_id = int(request.form.get("food_id"))
        grams = float(request.form.get("grams"))

        food = db.execute(
            "SELECT * FROM foods WHERE id = ?",
            (food_id,)
        ).fetchone()
        
        # Calculate macros based on grams
        protein = food["protein_100g"] * grams / 100
        carbs = food["carbs_100g"] * grams / 100
        fat = food["fat_100g"] * grams / 100
        # Calculate calories from food's calorie data (not from macros!)
        calories = food["calories_100g"] * grams / 100
        
        db.execute(
            """
            INSERT INTO meals (user_id, food_id, grams, protein_g, carbs_g, fat_g, calories)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, food_id, grams, protein, carbs, fat, calories)
        )
        db.commit()
        return redirect("/meals")

    # GET - fetch meals for selected date
    foods = db.execute("SELECT * FROM foods ORDER BY name")
    
    meals_list = db.execute(
        """
        SELECT meals.*, foods.name
        FROM meals
        JOIN foods ON meals.food_id = foods.id
        WHERE meals.user_id = ? AND DATE(meals.created_at) = ?
        ORDER BY meals.created_at DESC
        """,
        (user_id, current_date_str)
    )
    
    return render_template(
        "meals.html", 
        foods=foods, 
        meals=meals_list,
        current_date=current_date_str,
        current_date_formatted=current_date_formatted,
        prev_date=prev_date,
        next_date=next_date,
        today=today.strftime('%Y-%m-%d')
    )


@app.route("/edit_meal/<int:meal_id>", methods=["POST"])
@login_required
def edit_meal(meal_id):
    db = get_db()
    user_id = session["user_id"]
    
    # Get return date
    return_date = request.form.get("return_date", "")
    
    # Verify meal belongs to user
    meal = db.execute(
        "SELECT * FROM meals WHERE id = ? AND user_id = ?",
        (meal_id, user_id)
    ).fetchone()
    
    if not meal:
        return redirect("/meals" + (f"?date={return_date}" if return_date else ""))
    
    # Get new grams
    new_grams = float(request.form.get("grams"))
    
    if new_grams <= 0:
        return redirect("/meals" + (f"?date={return_date}" if return_date else ""))
    
    # Get food info
    food = db.execute(
        "SELECT * FROM foods WHERE id = ?",
        (meal["food_id"],)
    ).fetchone()
    
    # Recalculate macros and calories based on new grams
    protein = food["protein_100g"] * new_grams / 100
    carbs = food["carbs_100g"] * new_grams / 100
    fat = food["fat_100g"] * new_grams / 100
    # Use actual calorie data from food (not calculated from macros!)
    calories = food["calories_100g"] * new_grams / 100
    
    # Update database
    db.execute(
        """
        UPDATE meals 
        SET grams = ?, protein_g = ?, carbs_g = ?, fat_g = ?, calories = ?
        WHERE id = ? AND user_id = ?
        """,
        (new_grams, protein, carbs, fat, calories, meal_id, user_id)
    )
    db.commit()
    
    return redirect("/meals" + (f"?date={return_date}" if return_date else ""))


@app.route("/delete_meal/<int:meal_id>", methods=["POST"])
@login_required
def delete_meal(meal_id):
    db = get_db()
    user_id = session["user_id"]
    
    # Get return date
    return_date = request.form.get("return_date", "")
    
    # Verify meal belongs to user before deleting
    db.execute(
        "DELETE FROM meals WHERE id = ? AND user_id = ?",
        (meal_id, user_id)
    )
    db.commit()
    
    return redirect("/meals" + (f"?date={return_date}" if return_date else ""))


@app.route("/weight", methods=["GET", "POST"])
@login_required
def weight():
    db = get_db()
    user_id = session["user_id"]

    if request.method == "POST":
        weight_kg = float(request.form.get("weight_kg"))
        
        db.execute(
            "INSERT INTO weight (user_id, weight_kg) VALUES (?, ?)",
            (user_id, weight_kg)
        )
        db.commit()
        return redirect("/weight")

    # GET - last 30 records
    history = db.execute(
        """
        SELECT * FROM weight 
        WHERE user_id = ? 
        ORDER BY recorded_at DESC 
        LIMIT 30
        """,
        (user_id,)
    )

    return render_template("weight.html", history=history)


if __name__ == "__main__":
    app.run(debug=True)