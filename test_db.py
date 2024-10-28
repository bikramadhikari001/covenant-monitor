"""Test database operations without OpenAI integration."""
from flask import Flask
from src.models.database import db, Document, Covenant, Alert
import os
from datetime import datetime

def test_database():
    """Test basic database operations."""
    print("Testing database operations...")
    
    # Get absolute paths
    base_dir = os.path.abspath(os.path.dirname(__file__))
    instance_dir = os.path.join(base_dir, 'instance')
    db_path = os.path.join(instance_dir, 'covenant.db')
    
    # Create instance directory
    os.makedirs(instance_dir, exist_ok=True)
    
    # Create Flask app
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=f'sqlite:///{db_path}',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        try:
            # Create test document
            print("\nCreating test document...")
            doc = Document(
                filename='test.pdf',
                user_id='test_user',
                document_type='test',
                doc_metadata={'test': True}
            )
            db.session.add(doc)
            db.session.commit()
            print(f"Created document with ID: {doc.id}")
            
            # Create test covenant
            print("\nCreating test covenant...")
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
            print(f"Created covenant with ID: {covenant.id}")
            
            # Query and verify
            print("\nVerifying database records...")
            doc_check = Document.query.get(doc.id)
            print(f"Found document: {doc_check.filename}")
            
            covenant_check = Covenant.query.get(covenant.id)
            print(f"Found covenant: {covenant_check.name}")
            
            print("\nDatabase operations successful!")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_database()
