import os
import sqlite3
import sys
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-secret-development-key')

# Resolve database dependency
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

def get_db_connection():
    """
    Returns a unified database connection and type.
    Falls back to SQLite for local development/testing if PostgreSQL connection fails.
    """
    db_host = os.environ.get('DB_HOST')
    db_port = os.environ.get('DB_PORT', '5432')
    db_name = os.environ.get('DB_NAME')
    db_user = os.environ.get('DB_USER')
    db_pass = os.environ.get('DB_PASSWORD')

    # Try connecting to PostgreSQL if coordinates are provided
    if HAS_POSTGRES and db_host and db_name and db_user:
        try:
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_pass,
                connect_timeout=3
            )
            return conn, "postgres"
        except psycopg2.OperationalError as e:
            print(f"PostgreSQL Connection failed ({e}). Falling back to SQLite.", file=sys.stderr)

    # Local SQLite fallback
    sqlite_db = os.environ.get('SQLITE_DB', 'app.db')
    conn = sqlite3.connect(sqlite_db)
    conn.row_factory = sqlite3.Row
    return conn, "sqlite"

def execute_query(query, args=(), commit=False, fetch=True):
    """
    Executes a query using prepared statements with parameter binding.
    Translates standard '?' placeholders to '%s' dynamically for PostgreSQL compatibility.
    """
    conn, db_type = get_db_connection()
    cur = None
    try:
        if db_type == "postgres":
            # Translate sqlite parameter markers (?) to postgres format (%s)
            query = query.replace('?', '%s')
            cur = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cur = conn.cursor()

        cur.execute(query, args)

        if commit:
            conn.commit()
            result = None
        elif fetch:
            rows = cur.fetchall()
            result = [dict(row) for row in rows]
        else:
            result = None

        cur.close()
        conn.close()
        return result
    except Exception as e:
        if cur:
            cur.close()
        if conn:
            conn.rollback()
            conn.close()
        raise e

def init_db():
    """Initializes the database schema for the MVP application."""
    conn, db_type = get_db_connection()
    cur = conn.cursor()
    if db_type == "postgres":
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                status VARCHAR(20) DEFAULT 'todo',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    else:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'todo',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    conn.commit()
    cur.close()
    conn.close()

# Initialize DB on start
try:
    init_db()
except Exception as e:
    print(f"Error initializing database: {e}", file=sys.stderr)

@app.route('/')
def index():
    """Serve the beautifully styled MVP frontend."""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint for Docker orchestration and CI/CD."""
    return jsonify({"status": "healthy", "database": "active"}), 200

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Fetch all tasks securely from the database using parameter binding."""
    try:
        tasks = execute_query(
            "SELECT id, title, description, status, created_at FROM tasks ORDER BY created_at DESC"
        )
        return jsonify(tasks), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task securely. Validates inputs to prevent bad requests."""
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()

    if not title:
        return jsonify({"error": "Title is required"}), 400

    try:
        # Secure, parameter-bound INSERT query
        execute_query(
            "INSERT INTO tasks (title, description, status) VALUES (?, ?, ?)",
            (title, description, 'todo'),
            commit=True
        )
        return jsonify({"message": "Task created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    """Toggle a task's status securely between 'todo' and 'done' using parameter binding."""
    try:
        # Check current status
        tasks = execute_query("SELECT status FROM tasks WHERE id = ?", (task_id,))
        if not tasks:
            return jsonify({"error": "Task not found"}), 404

        current_status = tasks[0]['status']
        new_status = 'done' if current_status == 'todo' else 'todo'

        # Secure, parameter-bound UPDATE query
        execute_query(
            "UPDATE tasks SET status = ? WHERE id = ?",
            (new_status, task_id),
            commit=True
        )
        return jsonify({"message": f"Task marked as {new_status}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task securely using parameter binding."""
    try:
        # Check existence
        tasks = execute_query("SELECT id FROM tasks WHERE id = ?", (task_id,))
        if not tasks:
            return jsonify({"error": "Task not found"}), 404

        # Secure, parameter-bound DELETE query
        execute_query("DELETE FROM tasks WHERE id = ?", (task_id,), commit=True)
        return jsonify({"message": "Task deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Start the development server
    app.run(host='0.0.0.0', port=5000, debug=True)
