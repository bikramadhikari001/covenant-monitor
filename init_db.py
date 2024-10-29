"""Initialize the database."""
from flask import Flask
from src.models.database import db, Project, Document, Covenant, Alert
import os
import sqlite3
import stat
from datetime import datetime

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
        # Drop all tables if they exist
        print("Dropping existing tables...")
        db.drop_all()
        
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Create tables directly with SQLite to ensure proper schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create Project table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS project (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            user_id VARCHAR(50) NOT NULL,
            created_at DATETIME
        )
        """)
        
        # Create Document table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS document (
            id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL,
            filename VARCHAR(255) NOT NULL,
            file_url VARCHAR(500) NOT NULL,
            upload_date DATETIME,
            user_id VARCHAR(50) NOT NULL,
            document_type VARCHAR(50),
            doc_metadata TEXT,
            processing_status VARCHAR(20),
            FOREIGN KEY(project_id) REFERENCES project(id)
        )
        """)
        
        # Create Covenant table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS covenant (
            id INTEGER PRIMARY KEY,
            document_id INTEGER NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            threshold FLOAT,
            current_value FLOAT,
            status VARCHAR(20),
            last_checked DATETIME,
            covenant_metadata TEXT,
            FOREIGN KEY(document_id) REFERENCES document(id)
        )
        """)
        
        # Create Alert table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alert (
            id INTEGER PRIMARY KEY,
            covenant_id INTEGER NOT NULL,
            type VARCHAR(50) NOT NULL,
            message TEXT NOT NULL,
            created_at DATETIME,
            status VARCHAR(20),
            alert_metadata TEXT,
            FOREIGN KEY(covenant_id) REFERENCES covenant(id)
        )
        """)
        
        conn.commit()
        
        # Verify schema
        print("\nVerifying database schema...")
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
        
        # Set database file permissions
        os.chmod(db_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP)
        
        print("\nDatabase initialized successfully!")
        print(f"Database location: {db_path}")
        print(f"Database permissions: {oct(os.stat(db_path).st_mode)[-3:]}")

if __name__ == '__main__':
    init_database()
