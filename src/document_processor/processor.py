"""Document processor module."""
from src.models.database import db, Document, Covenant, Alert
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process documents and extract covenants."""
    
    def __init__(self, file_path, user_id, project_id=None):
        """Initialize processor."""
        self.file_path = file_path
        self.user_id = user_id
        self.project_id = project_id
        
    def process_and_store(self):
        """Process document and store results."""
        try:
            # Mock processing for now
            logger.info("Using mock parser")
            
            # Create document record
            document = Document(
                project_id=self.project_id,
                filename=self.file_path.split('/')[-1],
                upload_date=datetime.utcnow(),
                user_id=self.user_id,
                document_type='loan_agreement',
                doc_metadata={
                    'document_type': 'loan_agreement',
                    'parties': ['TECH INNOVATIONS INC.', 'FIRST NATIONAL BANK', 'THE LENDERS'],
                    'processed_at': datetime.utcnow().isoformat(),
                    'effective_date': datetime.utcnow().strftime('%Y-%m-%d')
                },
                processing_status='pending'
            )
            db.session.add(document)
            db.session.flush()  # Get document ID without committing
            
            # Create mock covenants
            covenants = [
                {
                    'name': 'Debt Service Coverage Ratio',
                    'description': 'Maintain a minimum debt service coverage ratio of 1.2x',
                    'threshold_value': 1.2,
                    'current_value': 1.5,
                    'measurement_frequency': 'quarterly'
                },
                {
                    'name': 'Leverage Ratio',
                    'description': 'Maintain a maximum leverage ratio of 3.5x',
                    'threshold_value': 3.5,
                    'current_value': 3.2,
                    'measurement_frequency': 'quarterly'
                },
                {
                    'name': 'Working Capital Ratio',
                    'description': 'Maintain minimum working capital ratio of 1.1x',
                    'threshold_value': 1.1,
                    'current_value': 1.3,
                    'measurement_frequency': 'monthly'
                },
                {
                    'name': 'Capital Expenditure Limit',
                    'description': 'Annual capital expenditure not to exceed $10M',
                    'threshold_value': 10000000,
                    'current_value': 8500000,
                    'measurement_frequency': 'annually'
                },
                {
                    'name': 'Minimum Net Worth',
                    'description': 'Maintain minimum net worth of $50M',
                    'threshold_value': 50000000,
                    'current_value': 55000000,
                    'measurement_frequency': 'quarterly'
                },
                {
                    'name': 'Interest Coverage Ratio',
                    'description': 'Maintain minimum interest coverage ratio of 3.0x',
                    'threshold_value': 3.0,
                    'current_value': 3.8,
                    'measurement_frequency': 'quarterly'
                }
            ]
            
            # Store covenants
            for covenant_data in covenants:
                covenant = Covenant(
                    document_id=document.id,
                    user_id=self.user_id,
                    name=covenant_data['name'],
                    description=covenant_data['description'],
                    threshold_value=covenant_data['threshold_value'],
                    current_value=covenant_data['current_value'],
                    measurement_frequency=covenant_data['measurement_frequency']
                )
                covenant.update_compliance_status()
                db.session.add(covenant)
            
            document.processing_status = 'completed'
            db.session.commit()
            
            # Create alerts after commit
            for covenant in document.covenants:
                if covenant.compliance_status in ['warning', 'breach']:
                    alert = Alert(
                        covenant_id=covenant.id,
                        user_id=self.user_id,
                        alert_type=covenant.compliance_status,
                        message=f"{covenant.name} is in {covenant.compliance_status} status. Current value: {covenant.current_value}, Threshold: {covenant.threshold_value}",
                        details={
                            'covenant_name': covenant.name,
                            'current_value': covenant.current_value,
                            'threshold_value': covenant.threshold_value,
                            'measurement_frequency': covenant.measurement_frequency,
                            'last_updated': None
                        }
                    )
                    db.session.add(alert)
            
            db.session.commit()
            
            logger.info(f"Stored document with {len(covenants)} covenants")
            return document
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}", exc_info=True)
            db.session.rollback()
            raise
