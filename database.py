import psycopg2
from psycopg2 import Error
import os
import psycopg2.extras

def get_db_connection():
    return psycopg2.connect(
        # These match the environment variables in docker-compose.yml
        host=os.environ.get('DB_HOST', 'localhost'),
        database=os.environ.get('DB_NAME', 'sqli_lab'),
        user=os.environ.get('DB_USER', 'lab_user'),
        password=os.environ.get('DB_PASS', 'lab_password'),
        cursor_factory=psycopg2.extras.DictCursor
    )

def login_user(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    # VULNERABLE: Direct string formatting
    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    cur.execute(query, (username, password))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user, query

def search_products(search_term):
    conn = get_db_connection()
    cur = conn.cursor()
    # VULNERABLE: String concatenation
    query = f"SELECT name, description, stock, image_url FROM products WHERE name LIKE '%{search_term}%' AND released = true"
    try:
        cur.execute(query)
        results = cur.fetchall()
        error = None
    except Exception as e:
        results = None
        error = str(e)
    finally:
        cur.close()
        conn.close()
    return results, query, error

def get_user_by_id(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    # VULNERABLE: Used for Blind SQLi
    query = f"SELECT username FROM users WHERE id = {user_id}"
    try:
        cur.execute(query)
        user = cur.fetchone()
    except:
        user = None
    finally:
        cur.close()
        conn.close()
    return user, query

 
def get_admin_stats():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM users")
    user_count = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM products")
    prod_count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {"users": user_count, "products": prod_count, "db_engine": "PostgreSQL 15.x"}

def get_system_logs():
    # Dummy sensitive data to show "Admin-only" info
    return [
        {"time": "10:45:01", "event": "Backup Completed", "user": "SYSTEM"},
        {"time": "11:20:15", "event": "Password Reset", "user": "alice"},
        {"time": "12:05:00", "event": "Database Config Exported", "user": "admin"},
        {"time": "13:10:22", "event": "Failed Login Attempt", "user": "unknown_ip"}
    ]