import pdfplumber
import json
from typing import List, Dict, Any, Union
from datetime import datetime
from openai import OpenAI
import os
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
        
    def extract_text(self) -> str:
        """Extract text from PDF document."""
        text = ""
        with pdfplumber.open(self.file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    
    def analyze_with_gpt(self, text: str) -> List[Dict[str, Any]]:
        """Use GPT to analyze and extract covenants from text."""
        system_prompt = """You are a financial analyst specializing in covenant analysis. Extract all financial covenants from loan documents.
        For each covenant, identify:
        1. Type (e.g., leverage_ratio, interest_coverage_ratio)
        2. Threshold value (can be a single value or multiple values with conditions)
        3. Description (clear explanation)
        4. Measurement frequency
        5. Calculation method
        
        Handle complex thresholds like:
        - Step-down ratios with dates
        - Multiple conditions
        - Currency amounts
        - Percentage values
        
        Return as a JSON array with consistent structure."""
        
        user_prompt = f"""Analyze this loan document and extract all financial covenants.
        For each covenant, provide:
        1. Type: snake_case identifier
        2. Threshold: Can be:
           - Single value (number)
           - Object with 'value' and conditions
           - Array of objects for step-down thresholds
        3. Description: Clear explanation of the requirement
        4. Measurement frequency: How often it's measured
        5. Calculation method: How it's calculated (if specified)

        Document text:
        {text[:8000]}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            covenants = json.loads(content)
            
            # Normalize the covenants
            normalized = []
            for covenant in covenants:
                try:
                    normalized.append(self.normalize_covenant(covenant))
                except Exception as e:
                    logger.error(f"Error normalizing covenant: {str(e)}")
                    continue
                    
            return normalized
            
        except Exception as e:
            logger.error(f"Error in GPT analysis: {str(e)}")
            return []
    
    def normalize_covenant(self, covenant: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize covenant data for database storage."""
        threshold = covenant.get('threshold')
        
        # Handle different threshold formats
        if isinstance(threshold, list):
            # Multiple thresholds (e.g., step-down ratios)
            covenant['thresholds'] = threshold
            covenant['threshold_value'] = threshold[0].get('value')  # Use first threshold
        elif isinstance(threshold, dict):
            # Single threshold with conditions
            covenant['thresholds'] = [threshold]
            covenant['threshold_value'] = threshold.get('value')
        else:
            # Simple threshold value
            covenant['threshold_value'] = threshold
            covenant['thresholds'] = [{'value': threshold}]
        
        # Convert ratio strings to float
        if isinstance(covenant['threshold_value'], str):
            covenant['threshold_value'] = self.parse_threshold_value(covenant['threshold_value'])
        
        # Normalize frequency
        covenant['measurement_frequency'] = self.normalize_frequency(
            covenant.get('frequency', 'not specified')
        )
        
        return covenant
    
    def parse_threshold_value(self, value: str) -> float:
        """Parse threshold value from string to float."""
        try:
            # Handle ratio format (e.g., "3.50:1.00")
            if ':' in value:
                num, denom = value.split(':')
                return float(num) / float(denom)
            
            # Handle currency format (e.g., "USD 10000000")
            value = value.replace('USD', '').replace(',', '').strip()
            
            # Handle percentage format
            if '%' in value:
                value = value.replace('%', '')
                return float(value) / 100
                
            return float(value)
        except:
            return 0.0
    
    def normalize_frequency(self, freq: str) -> str:
        """Normalize measurement frequency string."""
        freq = freq.lower()
        if 'quarter' in freq:
            return 'quarterly'
        elif 'month' in freq:
            return 'monthly'
        elif 'year' in freq or 'annual' in freq:
            return 'annually'
        elif 'all times' in freq:
            return 'continuous'
        else:
            return 'not specified'
    
    def process_document(self) -> Dict[str, Any]:
        """Main method to process document and extract all relevant information."""
        text = self.extract_text()
        
        # Use GPT to analyze the document
        covenants = self.analyze_with_gpt(text)
        
        # Extract dates using pattern matching as backup
        dates = self.extract_dates(text)
        
        # Get document metadata
        metadata = {
            'document_type': self.identify_document_type(text),
            'parties': self.extract_parties(text),
            'processed_at': datetime.utcnow().isoformat()
        }
        
        return {
            'covenants': covenants,
            'dates': dates,
            'metadata': metadata,
            'raw_text': text
        }
    
    def extract_dates(self, text: str) -> List[Dict[str, str]]:
        """Extract relevant dates from the document."""
        date_patterns = {
            'review_date': r'(?:review|reporting|compliance)\s*date.*?(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            'effective_date': r'(?:effective|closing)\s*date.*?(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            'termination_date': r'(?:termination|maturity)\s*date.*?(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
        }
        
        dates = []
        for date_type, pattern in date_patterns.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                dates.append({
                    'type': date_type,
                    'date': match.group(1),
                    'context': match.group(0)
                })
        
        return dates

    def identify_document_type(self, text: str) -> str:
        """Identify the type of document using GPT."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Identify financial document types."},
                    {"role": "user", "content": f"What type of financial document is this? Choose from: Loan Agreement, Bond Indenture, Credit Agreement, Amendment, Other (specify)\n\nFirst few paragraphs:\n{text[:1000]}"}
                ],
                temperature=0.1
            )
            return response.choices[0].message.content.strip().lower()
        except:
            return 'unknown'

    def extract_parties(self, text: str) -> List[str]:
        """Extract parties involved in the agreement using GPT."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Extract party names from legal documents."},
                    {"role": "user", "content": f"Identify the main parties (lender, borrower, etc.) in this agreement. Return as a JSON array of strings.\n\nFirst part of document:\n{text[:2000]}"}
                ],
                temperature=0.1
            )
            return json.loads(response.choices[0].message.content)
        except:
            return []
