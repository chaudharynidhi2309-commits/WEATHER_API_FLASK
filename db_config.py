import psycopg2
from psycopg2 import pool  # ✅ Make sure this import is present
from flask import jsonify

db_params = {
    "database": "weather_db",
    "user": "postgres",
    "password": "postgres",  # Add your actual password
    "host": "127.0.0.1",
    "port": "5432"
}

# Connection Pool Initialization
try:
    cpool = pool.SimpleConnectionPool(minconn=1, maxconn=100, **db_params)
    if cpool:
        print("✅ Connection pool established.")
except Exception as e:
    print(f"❌ Connection pool error: {e}")
    cpool = None

# Error Message Formatter
def error_message(error, msg):
    return {"error_details": error, "message": msg, "status": False}

# Connection Management
def close_conn(conn, cur):
    if cur: 
        cur.close()
    if conn: 
        cpool.putconn(conn)

# CRUD Query Function
def db_crud_query(insert_query, params=None):
    conn, cur = None, None
    try:
        conn = cpool.getconn()
        cur = conn.cursor()
        cur.execute(insert_query, params)
        conn.commit()
        return True
    except Exception as e:
        error = str(e)
        msg = 'Server Issue please contact Administration'
        error_res = error_message(error, msg)
        print("error_res", error_res)
        return error_res
    finally:
        close_conn(conn, cur)

# Fetch Query Function
def execute_fetch_query(fetch_query, params=None):
    conn, cur = None, None
    try:
        conn = cpool.getconn()
        cur = conn.cursor()
        cur.execute(fetch_query, params)
        data = cur.fetchall()
        return data
    except Exception as e:
        error = str(e)
        msg = 'Server Issue please contact Administration'
        error_res = error_message(error, msg)
        print("error_res", error_res)
        return None
    finally:
        close_conn(conn, cur)

# Test the connection
if __name__ == "__main__":
    print("Testing database connection...")