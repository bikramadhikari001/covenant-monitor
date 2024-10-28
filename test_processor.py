"""Test document processor with both mock and real parsers."""
from flask import Flask
from src.models.database import db
from src.document_processor.processor import DocumentProcessor
import os
from dotenv import load_dotenv

def test_processor():
    """Test document processor with both parsers."""
    print("Testing document processor...")
    
    # Load environment variables
    load_dotenv()
    
    # Get absolute paths
    base_dir = os.path.abspath(os.path.dirname(__file__))
    instance_dir = os.path.join(base_dir, 'instance')
    db_path = os.path.join(instance_dir, 'covenant.db')
    pdf_path = os.path.join(os.path.dirname(base_dir), 'loan-agreement.pdf')
    
    # Verify PDF exists
    if not os.path.exists(pdf_path):
        print(f"Error: Could not find loan agreement at {pdf_path}")
        return
    
    print(f"Using PDF file: {pdf_path}")
    
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
            
            # Test with mock parser
            print("\nTesting with mock parser...")
            mock_processor = DocumentProcessor(pdf_path, 'test_user', use_mock=True)
            mock_doc = mock_processor.process_and_store()
            print(f"Mock document stored with ID: {mock_doc.id}")
            print(f"Mock covenants: {len(mock_doc.covenants)}")
            
            print("\nMock Covenants:")
            for covenant in mock_doc.covenants:
                print(f"- {covenant.name}: {covenant.threshold_value}")
                print(f"  Description: {covenant.description}")
                print(f"  Frequency: {covenant.measurement_frequency}")
                print(f"  Next Review: {covenant.next_review_date}")
                print()
            
            # Test with real parser if API key is available
            if os.getenv('OPENAI_API_KEY'):
                print("\nTesting with OpenAI parser...")
                real_processor = DocumentProcessor(pdf_path, 'test_user', use_mock=False)
                real_doc = real_processor.process_and_store()
                print(f"Real document stored with ID: {real_doc.id}")
                print(f"Real covenants: {len(real_doc.covenants)}")
                
                print("\nReal Covenants:")
                for covenant in real_doc.covenants:
                    print(f"- {covenant.name}: {covenant.threshold_value}")
                    print(f"  Description: {covenant.description}")
                    print(f"  Frequency: {covenant.measurement_frequency}")
                    print(f"  Next Review: {covenant.next_review_date}")
                    print()
            else:
                print("\nSkipping OpenAI parser test (no API key)")
            
            print("\nTest completed successfully!")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_processor()
