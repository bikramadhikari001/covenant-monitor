"""Test core functionality of covenant extraction and storage."""
import os
from src.document_processor.processor import DocumentProcessor
from src.models.database import db
from dotenv import load_dotenv
import json
from app import create_app

def main():
    """Test document processing with sample loan agreement."""
    # Load environment variables
    load_dotenv(verbose=True)
    
    # Verify OpenAI API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables")
        return
        
    print(f"Using OpenAI API key: {api_key[:8]}...")
    
    # Get the absolute path to the loan agreement PDF
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(os.path.dirname(current_dir), 'loan-agreement.pdf')
    
    if not os.path.exists(pdf_path):
        print(f"Error: Could not find loan agreement at {pdf_path}")
        return
    
    # Create Flask app with absolute database path
    app = create_app()
    
    # Ensure instance directory exists with proper permissions
    instance_dir = os.path.join(current_dir, 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    os.chmod(instance_dir, 0o775)  # rwxrwxr-x
    
    with app.app_context():
        try:
            # Initialize processor
            print(f"\nProcessing document: {pdf_path}")
            processor = DocumentProcessor(pdf_path, user_id='test_user')
            
            # Process and store document
            document = processor.process_and_store()
            
            print(f"\nDocument processed and stored:")
            print(f"ID: {document.id}")
            print(f"Type: {document.document_type}")
            print(f"Metadata: {document.doc_metadata}")
            
            print("\nStored Covenants:")
            for covenant in document.covenants:
                print("\n---")
                print(f"Type: {covenant.name}")
                print(f"Threshold: {covenant.threshold_value}")
                print(f"Description: {covenant.description}")
                print(f"Next Review: {covenant.next_review_date}")
                print(f"Data Source: {covenant.data_source}")
            
            # Save results to file
            results = {
                'document_id': document.id,
                'document_type': document.document_type,
                'metadata': document.doc_metadata,
                'covenants': [{
                    'name': c.name,
                    'threshold': c.threshold_value,
                    'description': c.description,
                    'next_review': c.next_review_date.isoformat() if c.next_review_date else None,
                    'data_source': c.data_source
                } for c in document.covenants]
            }
            
            with open('extraction_results.json', 'w') as f:
                json.dump(results, f, indent=2)
            print("\nResults saved to extraction_results.json")
            
        except Exception as e:
            print(f"Error processing document: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()
