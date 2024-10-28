"""Test the system using mock document parser."""
from flask import Flask
from src.models.database import db, Document, Covenant, Alert
from src.document_processor.mock_parser import MockDocumentParser
import os
from datetime import datetime

def test_with_mock():
    """Test document processing with mock parser."""
    print("Testing document processing with mock parser...")
    
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
            # Create tables
            db.create_all()
            
            # Initialize mock parser
            parser = MockDocumentParser('mock_document.pdf')
            
            # Process document
            print("\nProcessing document...")
            results = parser.process_document()
            
            # Store document
            doc = Document(
                filename='mock_document.pdf',
                user_id='test_user',
                document_type=results['metadata']['document_type'],
                doc_metadata=results['metadata']
            )
            db.session.add(doc)
            db.session.flush()
            
            # Store covenants
            print("\nStoring covenants...")
            for covenant_data in results['covenants']:
                covenant = Covenant(
                    document_id=doc.id,
                    user_id='test_user',
                    name=covenant_data['type'],
                    description=covenant_data['description'],
                    threshold_value=covenant_data['threshold_value'],
                    measurement_frequency=covenant_data['measurement_frequency'],
                    compliance_status='pending'
                )
                db.session.add(covenant)
            
            db.session.commit()
            
            # Verify stored data
            print("\nVerifying stored data...")
            stored_doc = Document.query.first()
            print(f"Document: {stored_doc.filename} ({stored_doc.document_type})")
            
            stored_covenants = Covenant.query.all()
            print(f"\nStored {len(stored_covenants)} covenants:")
            for covenant in stored_covenants:
                print(f"- {covenant.name}: {covenant.threshold_value}")
            
            print("\nTest completed successfully!")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_with_mock()
