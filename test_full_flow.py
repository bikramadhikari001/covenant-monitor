"""Test full flow of database operations."""
import os
import sqlite3
from flask import Flask
from src.models.database import db, Document, Covenant, Alert
from datetime import datetime

def test_database_operations():
    """Test database operations step by step."""
    print("\n=== Testing Database Operations ===\n")
    
    # Step 1: Setup paths
    base_dir = os.path.abspath(os.path.dirname(__file__))
    instance_dir = os.path.join(base_dir, 'instance')
    db_path = os.path.join(instance_dir, 'covenant.db')
    
    print(f"Base directory: {base_dir}")
    print(f"Instance directory: {instance_dir}")
    print(f"Database path: {db_path}")
    
    # Step 2: Create instance directory
    print("\n--- Setting up directories ---")
    os.makedirs(instance_dir, exist_ok=True)
    os.chmod(instance_dir, 0o775)
    print(f"Instance directory permissions: {oct(os.stat(instance_dir).st_mode)[-3:]}")
    
    # Step 3: Remove existing database
    if os.path.exists(db_path):
        print("\n--- Removing existing database ---")
        os.remove(db_path)
    
    # Step 4: Create Flask app and initialize database
    print("\n--- Initializing Flask app and database ---")
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        
        # Verify database file
        if os.path.exists(db_path):
            print(f"Database created successfully")
            print(f"Database permissions: {oct(os.stat(db_path).st_mode)[-3:]}")
            os.chmod(db_path, 0o664)
            print(f"Updated database permissions: {oct(os.stat(db_path).st_mode)[-3:]}")
        else:
            print("Error: Database file not created")
            return
        
        # Step 5: Test database operations
        print("\n--- Testing database operations ---")
        try:
            # Create test document
            doc = Document(
                filename='test.pdf',
                upload_date=datetime.utcnow(),
                user_id='test_user',
                document_type='test',
                doc_metadata={'test': True}
            )
            db.session.add(doc)
            db.session.commit()
            print("Successfully created test document")
            
            # Create test covenant
            covenant = Covenant(
                document_id=doc.id,
                user_id='test_user',
                name='Test Covenant',
                description='Test Description',
                threshold_value=1.0,
                current_value=0.5,
                compliance_status='compliant',
                measurement_frequency='monthly'
            )
            db.session.add(covenant)
            db.session.commit()
            print("Successfully created test covenant")
            
            # Query test data
            print("\n--- Verifying data ---")
            doc_check = Document.query.first()
            print(f"Found document: {doc_check.filename}")
            
            covenant_check = Covenant.query.first()
            print(f"Found covenant: {covenant_check.name}")
            
        except Exception as e:
            print(f"Error during database operations: {str(e)}")
            return
        
        # Step 6: Verify database structure
        print("\n--- Verifying database structure ---")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"Tables in database: {', '.join(table[0] for table in tables)}")
            
            # Get Document table schema
            cursor.execute("PRAGMA table_info(document);")
            columns = cursor.fetchall()
            print("\nDocument table columns:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            
            conn.close()
            
        except Exception as e:
            print(f"Error verifying database structure: {str(e)}")
            return
    
    print("\n=== Test completed successfully! ===")

if __name__ == '__main__':
    test_database_operations()
