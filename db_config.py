"""
Database Configuration Module
Handles PostgreSQL connection pooling and query execution
"""
import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration from environment
db_params = {
    "database": os.getenv("DB_NAME", "weather_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": os.getenv("DB_PORT", "5432")
}

# Initialize connection pool
try:
    cpool = pool.SimpleConnectionPool(minconn=1, maxconn=100, **db_params)
    print("✅ Database connection pool established")
except Exception as e:
    print(f"❌ Connection pool error: {e}")
    cpool = None
    raise ConnectionError("Failed to establish database connection pool")


def error_message(error: str, msg: str) -> dict:
    """Format error messages consistently"""
    return {
        "error_details": error,
        "message": msg,
        "status": False
    }


def close_conn(conn, cur) -> None:
    """Safely close database cursor and return connection to pool"""
    if cur:
        cur.close()
    if conn:
        cpool.putconn(conn)


def db_crud_query(query: str, params: tuple = None) -> bool or dict:
    """
    Execute INSERT/UPDATE/DELETE queries
    
    Args:
        query: SQL query string with placeholders
        params: Tuple of parameters for the query
        
    Returns:
        True if successful, error dict otherwise
    """
    conn, cur = None, None
    try:
        conn = cpool.getconn()
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        error_res = error_message(str(e), "Database operation failed")
        print(f"❌ CRUD Error: {error_res}")
        return error_res
    finally:
        close_conn(conn, cur)


def execute_fetch_query(query: str, params: tuple = None) -> list or None:
    """
    Execute SELECT queries
    
    Args:
        query: SQL query string with placeholders
        params: Tuple of parameters for the query
        
    Returns:
        List of tuples containing query results, None if error
    """
    conn, cur = None, None
    try:
        conn = cpool.getconn()
        cur = conn.cursor()
        cur.execute(query, params)
        data = cur.fetchall()
        return data
    except Exception as e:
        error_res = error_message(str(e), "Database query failed")
        print(f"❌ Fetch Error: {error_res}")
        return None
    finally:
        close_conn(conn, cur)