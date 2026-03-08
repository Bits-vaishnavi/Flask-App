from flask import Flask, request, jsonify
from flasgger import Swagger
import sqlite3
import random
from datetime import date

app = Flask(__name__)
swagger = Swagger(app)

DB_NAME = "aceest_fitness.db"

PROGRAMS = {
    "Fat Loss": {
        "workout": "Mon: 5x5 Back Squat + AMRAP | Tue: EMOM 20min Assault Bike | Wed: Bench Press + 21-15-9 | Thu: 10RFT Deadlifts/Box Jumps | Fri: 30min Active Recovery",
        "diet": "B: 3 Egg Whites + Oats Idli | L: Grilled Chicken + Brown Rice | D: Fish Curry + Millet Roti | Target: 2,000 kcal",
        "target_calories": 2000
    },
    "Muscle Gain": {
        "workout": "Mon: Squat 5x5 | Tue: Bench 5x5 | Wed: Deadlift 4x6 | Thu: Front Squat 4x8 | Fri: Incline Press 4x10 | Sat: Barbell Rows 4x10",
        "diet": "B: 4 Eggs + PB Oats | L: Chicken Biryani (250g Chicken) | D: Mutton Curry + Jeera Rice | Target: 3,200 kcal",
        "target_calories": 3200
    },
    "Beginner": {
        "workout": "Circuit Training: Air Squats, Ring Rows, Push-ups | Focus: Technique Mastery and Form",
        "diet": "Balanced Tamil Meals: Idli-Sambar, Rice-Dal, Chapati | Protein: 120g/day",
        "target_calories": 2200
    }
}

PROGRAM_TEMPLATES = {
    "Fat Loss": ["Full Body HIIT", "Circuit Training", "Cardio + Weights"],
    "Muscle Gain": ["Push/Pull/Legs", "Upper/Lower Split", "Full Body Strength"],
    "Beginner": ["Full Body 3x/week", "Light Strength + Mobility"]
}


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY, password TEXT, role TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, age INTEGER,
        height REAL, weight REAL, program TEXT, calories INTEGER,
        target_weight REAL, target_adherence INTEGER,
        membership_status TEXT DEFAULT 'Active', membership_end TEXT)""")

    # Ensure the clients table has the expected columns (migrations for existing DBs)
    cur.execute("PRAGMA table_info(clients)")
    existing_cols = {row[1] for row in cur.fetchall()}
    expected_columns = {
        "height": "REAL",
        "weight": "REAL",
        "program": "TEXT",
        "calories": "INTEGER",
        "target_weight": "REAL",
        "target_adherence": "INTEGER",
        "membership_status": "TEXT DEFAULT 'Active'",
        "membership_end": "TEXT"
    }
    for col, col_def in expected_columns.items():
        if col not in existing_cols:
            cur.execute(f"ALTER TABLE clients ADD COLUMN {col} {col_def}")

    cur.execute("""CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, week TEXT, adherence INTEGER)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, date TEXT,
        workout_type TEXT, duration_min INTEGER, notes TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, date TEXT,
        weight REAL, waist REAL, bodyfat REAL)""")
    cur.execute("SELECT * FROM users WHERE username='admin'")
    if not cur.fetchone():
        cur.execute("INSERT INTO users VALUES ('admin','admin','Admin')")
    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


with app.app_context():
    init_db()


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/", methods=["GET"])
def health_check():
    """Health Check
    Returns basic API status.
    ---
    tags:
      - Health
    responses:
      200:
        description: API is running
    """
    return jsonify({"app": "ACEest Fitness and Gym API", "status": "running", "version": "1.0.0"}), 200


# ============================================================
# PROGRAMS
# ============================================================

@app.route("/programs", methods=["GET"])
def get_programs():
    """Get all fitness programs
    Returns all programs with workout and diet plans.
    ---
    tags:
      - Programs
    responses:
      200:
        description: List of all programs
    """
    return jsonify({"programs": PROGRAMS}), 200


@app.route("/programs/<name>", methods=["GET"])
def get_program(name):
    """Get a specific program by name
    ---
    tags:
      - Programs
    parameters:
      - name: name
        in: path
        type: string
        required: true
        description: Program name (Fat Loss, Muscle Gain, Beginner)
        enum: [Fat Loss, Muscle Gain, Beginner]
    responses:
      200:
        description: Program details
      404:
        description: Program not found
    """
    program = PROGRAMS.get(name)
    if not program:
        return jsonify({"error": f"Program '{name}' not found"}), 404
    return jsonify({"program": name, "details": program}), 200


# ============================================================
# CLIENTS
# ============================================================

@app.route("/clients", methods=["GET"])
def get_clients():
    """Get all clients
    ---
    tags:
      - Clients
    responses:
      200:
        description: List of all clients
    """
    conn = get_db()
    clients = conn.execute("SELECT * FROM clients ORDER BY name").fetchall()
    conn.close()
    return jsonify({"clients": [dict(c) for c in clients]}), 200


@app.route("/clients/<name>", methods=["GET"])
def get_client(name):
    """Get a single client by name
    ---
    tags:
      - Clients
    parameters:
      - name: name
        in: path
        type: string
        required: true
        description: Client name
    responses:
      200:
        description: Client details
      404:
        description: Client not found
    """
    conn = get_db()
    client = conn.execute("SELECT * FROM clients WHERE name=?", (name,)).fetchone()
    conn.close()
    if not client:
        return jsonify({"error": f"Client '{name}' not found"}), 404
    return jsonify({"client": dict(client)}), 200


@app.route("/clients", methods=["POST"])
def add_client():
    """Add a new client
    ---
    tags:
      - Clients
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              example: Arjun
            age:
              type: integer
              example: 25
            height:
              type: number
              example: 175.0
            weight:
              type: number
              example: 75.0
            program:
              type: string
              example: Fat Loss
            calories:
              type: integer
              example: 2000
            target_weight:
              type: number
              example: 70.0
            target_adherence:
              type: integer
              example: 80
            membership_status:
              type: string
              example: Active
            membership_end:
              type: string
              example: "2025-12-31"
    responses:
      201:
        description: Client added successfully
      400:
        description: Missing required field
      409:
        description: Client already exists
    """
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Field 'name' is required"}), 400
    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO clients (name, age, height, weight, program, calories,
                target_weight, target_adherence, membership_status, membership_end)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (data["name"], data.get("age"), data.get("height"), data.get("weight"),
             data.get("program"), data.get("calories"), data.get("target_weight"),
             data.get("target_adherence"), data.get("membership_status", "Active"),
             data.get("membership_end")))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": f"Client '{data['name']}' already exists"}), 409
    conn.close()
    return jsonify({"message": f"Client '{data['name']}' added successfully"}), 201


@app.route("/clients/<name>", methods=["PUT"])
def update_client(name):
    """Update a client's details
    ---
    tags:
      - Clients
    parameters:
      - name: name
        in: path
        type: string
        required: true
        description: Client name to update
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            age:
              type: integer
            height:
              type: number
            weight:
              type: number
            program:
              type: string
            calories:
              type: integer
            target_weight:
              type: number
            target_adherence:
              type: integer
            membership_status:
              type: string
            membership_end:
              type: string
    responses:
      200:
        description: Client updated
      404:
        description: Client not found
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    conn = get_db()
    client = conn.execute("SELECT * FROM clients WHERE name=?", (name,)).fetchone()
    if not client:
        conn.close()
        return jsonify({"error": f"Client '{name}' not found"}), 404
    allowed_fields = ["age", "height", "weight", "program", "calories",
                      "target_weight", "target_adherence", "membership_status", "membership_end"]
    updates = {f: data[f] for f in allowed_fields if f in data}
    if updates:
        set_clause = ", ".join(f"{k}=?" for k in updates)
        conn.execute(f"UPDATE clients SET {set_clause} WHERE name=?",
                     list(updates.values()) + [name])
        conn.commit()
    conn.close()
    return jsonify({"message": f"Client '{name}' updated successfully"}), 200


@app.route("/clients/<name>", methods=["DELETE"])
def delete_client(name):
    """Delete a client
    ---
    tags:
      - Clients
    parameters:
      - name: name
        in: path
        type: string
        required: true
        description: Client name to delete
    responses:
      200:
        description: Client deleted
      404:
        description: Client not found
    """
    conn = get_db()
    result = conn.execute("DELETE FROM clients WHERE name=?", (name,))
    conn.commit()
    conn.close()
    if result.rowcount == 0:
        return jsonify({"error": f"Client '{name}' not found"}), 404
    return jsonify({"message": f"Client '{name}' deleted"}), 200


@app.route("/clients/<name>/generate-program", methods=["POST"])
def generate_program(name):
    """Auto-assign a random training program to a client
    ---
    tags:
      - Clients
    parameters:
      - name: name
        in: path
        type: string
        required: true
        description: Client name
    responses:
      200:
        description: Program generated and assigned
      404:
        description: Client not found
    """
    conn = get_db()
    client = conn.execute("SELECT * FROM clients WHERE name=?", (name,)).fetchone()
    if not client:
        conn.close()
        return jsonify({"error": f"Client '{name}' not found"}), 404
    program_type = random.choice(list(PROGRAM_TEMPLATES.keys()))
    program_detail = random.choice(PROGRAM_TEMPLATES[program_type])
    conn.execute("UPDATE clients SET program=? WHERE name=?", (program_detail, name))
    conn.commit()
    conn.close()
    return jsonify({
        "message": f"Program generated for '{name}'",
        "program_type": program_type,
        "program": program_detail
    }), 200


@app.route("/clients/<name>/membership", methods=["GET"])
def check_membership(name):
    """Check membership status and renewal date for a client
    ---
    tags:
      - Clients
    parameters:
      - name: name
        in: path
        type: string
        required: true
        description: Client name
    responses:
      200:
        description: Membership info
      404:
        description: Client not found
    """
    conn = get_db()
    client = conn.execute(
        "SELECT membership_status, membership_end FROM clients WHERE name=?", (name,)
    ).fetchone()
    conn.close()
    if not client:
        return jsonify({"error": f"Client '{name}' not found"}), 404
    return jsonify({
        "client": name,
        "membership_status": client["membership_status"],
        "membership_end": client["membership_end"]
    }), 200


# ============================================================
# PROGRESS
# ============================================================

@app.route("/progress/<client_name>", methods=["GET"])
def get_progress(client_name):
    """Get weekly adherence progress for a client
    ---
    tags:
      - Progress
    parameters:
      - name: client_name
        in: path
        type: string
        required: true
        description: Client name
    responses:
      200:
        description: Weekly progress records
    """
    conn = get_db()
    rows = conn.execute(
        "SELECT week, adherence FROM progress WHERE client_name=? ORDER BY id", (client_name,)
    ).fetchall()
    conn.close()
    return jsonify({"client": client_name, "progress": [dict(r) for r in rows]}), 200


@app.route("/progress/<client_name>", methods=["POST"])
def add_progress(client_name):
    """Log weekly adherence for a client
    ---
    tags:
      - Progress
    parameters:
      - name: client_name
        in: path
        type: string
        required: true
        description: Client name
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - week
            - adherence
          properties:
            week:
              type: string
              example: "Week 1"
            adherence:
              type: integer
              example: 85
              description: Value between 0 and 100
    responses:
      201:
        description: Progress logged
      400:
        description: Missing or invalid fields
    """
    data = request.get_json()
    if not data or "week" not in data or "adherence" not in data:
        return jsonify({"error": "Fields 'week' and 'adherence' are required"}), 400
    adherence = data["adherence"]
    if not isinstance(adherence, int) or not (0 <= adherence <= 100):
        return jsonify({"error": "Adherence must be an integer between 0 and 100"}), 400
    conn = get_db()
    conn.execute("INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)",
                 (client_name, data["week"], adherence))
    conn.commit()
    conn.close()
    return jsonify({"message": "Progress logged successfully"}), 201


# ============================================================
# WORKOUTS
# ============================================================

@app.route("/workouts/<client_name>", methods=["GET"])
def get_workouts(client_name):
    """Get all workout logs for a client
    ---
    tags:
      - Workouts
    parameters:
      - name: client_name
        in: path
        type: string
        required: true
        description: Client name
    responses:
      200:
        description: List of workout sessions
    """
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM workouts WHERE client_name=? ORDER BY date DESC", (client_name,)
    ).fetchall()
    conn.close()
    return jsonify({"client": client_name, "workouts": [dict(r) for r in rows]}), 200


@app.route("/workouts/<client_name>", methods=["POST"])
def add_workout(client_name):
    """Log a workout session for a client
    ---
    tags:
      - Workouts
    parameters:
      - name: client_name
        in: path
        type: string
        required: true
        description: Client name
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - workout_type
          properties:
            workout_type:
              type: string
              example: Strength
              enum: [Strength, Hypertrophy, Cardio, Mobility]
            date:
              type: string
              example: "2025-06-01"
            duration_min:
              type: integer
              example: 60
            notes:
              type: string
              example: "5x5 Squat day"
    responses:
      201:
        description: Workout logged
      400:
        description: Missing required field
    """
    data = request.get_json()
    if not data or not data.get("workout_type"):
        return jsonify({"error": "Field 'workout_type' is required"}), 400
    conn = get_db()
    conn.execute(
        "INSERT INTO workouts (client_name, date, workout_type, duration_min, notes) VALUES (?, ?, ?, ?, ?)",
        (client_name, data.get("date", date.today().isoformat()),
         data["workout_type"], data.get("duration_min", 60), data.get("notes", ""))
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Workout logged successfully"}), 201


# ============================================================
# METRICS
# ============================================================

@app.route("/metrics/<client_name>", methods=["GET"])
def get_metrics(client_name):
    """Get body metrics history for a client
    ---
    tags:
      - Metrics
    parameters:
      - name: client_name
        in: path
        type: string
        required: true
        description: Client name
    responses:
      200:
        description: Body metrics history
    """
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM metrics WHERE client_name=? ORDER BY date DESC", (client_name,)
    ).fetchall()
    conn.close()
    return jsonify({"client": client_name, "metrics": [dict(r) for r in rows]}), 200


@app.route("/metrics/<client_name>", methods=["POST"])
def add_metrics(client_name):
    """Log body metrics for a client
    ---
    tags:
      - Metrics
    parameters:
      - name: client_name
        in: path
        type: string
        required: true
        description: Client name
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            weight:
              type: number
              example: 74.5
              description: Weight in kg
            waist:
              type: number
              example: 82.0
              description: Waist in cm
            bodyfat:
              type: number
              example: 18.5
              description: Body fat percentage
            date:
              type: string
              example: "2025-06-01"
    responses:
      201:
        description: Metrics logged
      400:
        description: No data provided
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    conn = get_db()
    conn.execute(
        "INSERT INTO metrics (client_name, date, weight, waist, bodyfat) VALUES (?, ?, ?, ?, ?)",
        (client_name, data.get("date", date.today().isoformat()),
         data.get("weight"), data.get("waist"), data.get("bodyfat"))
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Metrics logged successfully"}), 201


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
