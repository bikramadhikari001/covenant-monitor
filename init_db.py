"""Initialize the database."""
from flask import Flask
from src.models.database import db, Document, Covenant, Alert
import os
import sqlite3
import stat

def init_database():
    """Initialize the database with tables."""
    print("Initializing database...")
    
    # Get absolute paths
    base_dir = os.path.abspath(os.path.dirname(__file__))
    instance_dir = os.path.join(base_dir, 'instance')
    db_path = os.path.join(instance_dir, 'covenant.db')
    
    # Create instance directory with proper permissions
    print(f"Creating instance directory at: {instance_dir}")
    os.makedirs(instance_dir, exist_ok=True)
    os.chmod(instance_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
    
    # Remove existing database
    if os.path.exists(db_path):
        print("Removing existing database...")
        os.remove(db_path)
    
    # Create a minimal Flask application
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{db_path}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        INSTANCE_PATH=instance_dir
    )
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Set database file permissions
        os.chmod(db_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP)
        
        # Verify schema using SQLite directly
        print("\nVerifying database schema...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Created tables: {', '.join(table[0] for table in tables)}")
        
        # Get Document table schema
        cursor.execute("PRAGMA table_info(document);")
        columns = cursor.fetchall()
        print("\nDocument table columns:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        conn.close()
        print("\nDatabase initialized successfully!")
        print(f"Database location: {db_path}")
        print(f"Database permissions: {oct(os.stat(db_path).st_mode)[-3:]}")

if __name__ == '__main__':
    init_database()
