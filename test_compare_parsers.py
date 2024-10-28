"""Compare outputs of mock and OpenAI parsers."""
from flask import Flask
from src.document_processor.processor import DocumentProcessor
import os
from dotenv import load_dotenv
import json
from datetime import datetime

def compare_parsers():
    """Compare outputs of mock and OpenAI parsers."""
    print("Comparing parser outputs...")
    
    # Load environment variables
    load_dotenv()
    
    # Get absolute paths
    base_dir = os.path.abspath(os.path.dirname(__file__))
    pdf_path = os.path.join(os.path.dirname(base_dir), 'loan-agreement.pdf')
    
    # Verify PDF exists
    if not os.path.exists(pdf_path):
        print(f"Error: Could not find loan agreement at {pdf_path}")
        return
    
    # Get results from both parsers
    mock_parser = DocumentProcessor(pdf_path, 'test_user', use_mock=True).parser
    mock_results = mock_parser.process_document()
    
    if os.getenv('OPENAI_API_KEY'):
        real_parser = DocumentProcessor(pdf_path, 'test_user', use_mock=False).parser
        real_results = real_parser.process_document()
        
        # Compare results
        print("\nComparing covenant extraction:")
        print(f"Mock covenants: {len(mock_results['covenants'])}")
        print(f"OpenAI covenants: {len(real_results['covenants'])}")
        
        # Compare covenant types
        mock_types = {c['type'] for c in mock_results['covenants']}
        real_types = {c['type'] for c in real_results['covenants']}
        
        print("\nCovenant types found by both parsers:")
        common_types = mock_types & real_types
        for type_ in sorted(common_types):
            print(f"- {type_}")
        
        print("\nTypes only in mock parser:")
        for type_ in sorted(mock_types - real_types):
            print(f"- {type_}")
        
        print("\nTypes only in OpenAI parser:")
        for type_ in sorted(real_types - mock_types):
            print(f"- {type_}")
        
        # Compare threshold values
        print("\nComparing threshold values:")
        for type_ in common_types:
            mock_covenant = next(c for c in mock_results['covenants'] if c['type'] == type_)
            real_covenant = next(c for c in real_results['covenants'] if c['type'] == type_)
            
            print(f"\n{type_}:")
            print(f"  Mock: {mock_covenant['threshold_value']}")
            print(f"  OpenAI: {real_covenant['threshold_value']}")
            if mock_covenant['threshold_value'] != real_covenant['threshold_value']:
                print("  ⚠️ Values differ!")
        
        # Save comparison results
        comparison = {
            'timestamp': datetime.utcnow().isoformat(),
            'mock_results': mock_results,
            'openai_results': real_results,
            'analysis': {
                'common_types': list(common_types),
                'mock_only': list(mock_types - real_types),
                'openai_only': list(real_types - mock_types)
            }
        }
        
        with open('parser_comparison.json', 'w') as f:
            json.dump(comparison, f, indent=2)
        print("\nComparison results saved to parser_comparison.json")
        
    else:
        print("\nSkipping comparison (no OpenAI API key)")
        print("\nMock parser results:")
        for covenant in mock_results['covenants']:
            print(f"\n{covenant['type']}:")
            print(f"  Threshold: {covenant['threshold_value']}")
            print(f"  Frequency: {covenant['measurement_frequency']}")

if __name__ == '__main__':
    compare_parsers()
