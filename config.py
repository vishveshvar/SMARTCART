"""
SmartCart - Application Configuration
Supports MySQL (smartcart_db) with seamless SQLite fallback.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "smartcart-ai-recommendation-secret-key-2026")
    
    # MySQL connection string default
    # Can be overridden with DATABASE_URL environment variable
    # e.g.: mysql+pymysql://root:password@localhost/smartcart_db
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = os.environ.get("MYSQL_PORT", "3306")
    MYSQL_DB = os.environ.get("MYSQL_DB", "smartcart_db")
    
    # Priority:
    # 1. DATABASE_URL env var if set
    # 2. SQLite if USE_SQLITE is true or if MySQL is unreachable
    # 3. MySQL
    USE_SQLITE = os.environ.get("USE_SQLITE", "false").lower() in ["true", "1", "yes"]
    
    SQLITE_PATH = os.path.join(BASE_DIR, "smartcart.db")
    
    if USE_SQLITE:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{SQLITE_PATH}"
    else:
        # Check explicit env var first
        env_db_url = os.environ.get("DATABASE_URL")
        if env_db_url:
            SQLALCHEMY_DATABASE_URI = env_db_url
        else:
            # We attempt MySQL, with a resilient fallback in database.py
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{SQLITE_PATH}"
            
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = "filesystem"
    JSON_SORT_KEYS = False
