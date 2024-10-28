from src.document_processor.parser import DocumentParser
import json

def test_document_processing():
    """Test document processing with sample loan agreement."""
    try:
        # Initialize parser with sample document
        parser = DocumentParser('../loan-agreement.pdf')
        
        # Process document
        print("Processing document...")
        results = parser.process_document()
        
        # Print extracted covenants
        print("\nExtracted Covenants:")
        for covenant in results['covenants']:
            print(f"\nCovenant Type: {covenant['type']}")
            print(f"Threshold Value: {covenant['threshold_value']}")
            print(f"Description: {covenant['description']}")
            if 'measurement_frequency' in covenant:
                print(f"Measurement Frequency: {covenant['measurement_frequency']}")
        
        # Print dates
        print("\nExtracted Dates:")
        for date in results['dates']:
            print(f"\nContext: {date['context']}")
            print(f"Date: {date['date']}")
        
        # Save results to file
        with open('extraction_results.json', 'w') as f:
            json.dump(results, f, indent=2)
            print("\nResults saved to extraction_results.json")
            
    except Exception as e:
        print(f"Error processing document: {str(e)}")

if __name__ == "__main__":
    test_document_processing()
