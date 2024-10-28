"""Mock document parser for testing without OpenAI API."""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import re

class MockDocumentParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def extract_text(self) -> str:
        """Mock text extraction."""
        return """
        SYNDICATED LOAN AGREEMENT
        
        THIS SYNDICATED LOAN AGREEMENT is made and entered into as of October 28, 2024, by and among:
        
        TECH INNOVATIONS INC., a Delaware corporation ("Borrower");
        FIRST NATIONAL BANK, as Administrative Agent ("Agent");
        THE LENDERS listed in Schedule A hereto.
        
        The Borrower shall maintain:
        1. Leverage Ratio not exceeding 3.5:1.0
        2. Interest Coverage Ratio of at least 3.0:1.0
        3. Minimum Liquidity of $10,000,000
        4. Capital Expenditures not exceeding $25,000,000 per fiscal year
        5. No distributions if Leverage Ratio exceeds 2.75:1.0
        6. No additional indebtedness exceeding $10,000,000 without consent
        """
    
    def process_document(self) -> Dict[str, Any]:
        """Mock document processing with predefined covenants."""
        # Mock covenants that match OpenAI parser output
        covenants = [
            {
                'type': 'leverage_ratio',
                'threshold_value': 3.5,
                'description': 'The Borrower shall maintain a Leverage Ratio not exceeding 3.5:1.0',
                'measurement_frequency': 'quarterly'
            },
            {
                'type': 'interest_coverage_ratio',
                'threshold_value': 3.0,
                'description': 'The Borrower shall maintain an Interest Coverage Ratio of not less than 3.0:1.0',
                'measurement_frequency': 'quarterly'
            },
            {
                'type': 'minimum_liquidity',
                'threshold_value': 10000000,
                'description': 'The Borrower shall maintain minimum Liquidity of not less than USD 10,000,000',
                'measurement_frequency': 'continuous'
            },
            {
                'type': 'capital_expenditures',
                'threshold_value': 25000000,
                'description': 'The Borrower shall not make or commit to make capital expenditures exceeding USD 25,000,000 in any fiscal year',
                'measurement_frequency': 'annually'
            },
            {
                'type': 'distributions',
                'threshold_value': 2.75,
                'description': 'The Borrower shall not declare or pay dividends if the Leverage Ratio exceeds 2.75:1.0',
                'measurement_frequency': 'quarterly'
            },
            {
                'type': 'additional_indebtedness',
                'threshold_value': 10000000,
                'description': 'The Borrower shall not incur additional indebtedness exceeding USD 10,000,000 without prior consent',
                'measurement_frequency': 'continuous'
            }
        ]
        
        # Mock metadata
        metadata = {
            'document_type': 'loan_agreement',
            'parties': ['TECH INNOVATIONS INC.', 'FIRST NATIONAL BANK', 'THE LENDERS'],
            'processed_at': datetime.utcnow().isoformat(),
            'effective_date': '2024-10-28'
        }
        
        return {
            'covenants': covenants,
            'metadata': metadata,
            'dates': [
                {
                    'type': 'effective_date',
                    'date': '2024-10-28',
                    'context': 'Agreement date'
                },
                {
                    'type': 'first_measurement',
                    'date': '2024-12-31',
                    'context': 'First measurement date'
                }
            ]
        }
    
    def identify_document_type(self, text: str) -> str:
        """Mock document type identification."""
        return 'loan_agreement'
    
    def extract_parties(self, text: str) -> List[str]:
        """Mock party extraction."""
        return ['TECH INNOVATIONS INC.', 'FIRST NATIONAL BANK', 'THE LENDERS']
