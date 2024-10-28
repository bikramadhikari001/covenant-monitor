import unittest
from app import create_app
from src.models.database import db, Document, Covenant, Alert
from src.document_processor.parser import DocumentParser
import os
import json

class CovenantMonitorTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            
    def test_document_upload_and_processing(self):
        """Test document upload and GPT processing"""
        # Sample loan document path
        doc_path = 'loan-agreement.pdf'
        
        with self.app.app_context():
            # Test document upload
            with open(doc_path, 'rb') as f:
                response = self.client.post('/upload', data={
                    'document': (f, 'loan-agreement.pdf')
                })
                self.assertEqual(response.status_code, 302)  # Redirect after success
                
            # Verify document was processed
            doc = Document.query.first()
            self.assertIsNotNone(doc)
            
            # Verify covenants were extracted
            covenants = Covenant.query.all()
            self.assertTrue(len(covenants) > 0)
            
    def test_gpt_analysis(self):
        """Test GPT-powered covenant analysis"""
        with self.app.app_context():
            # Create test covenant
            covenant = Covenant(
                name='Debt to Equity Ratio',
                description='Maintain debt-to-equity ratio below 2.5',
                threshold_value=2.5,
                current_value=2.7,
                compliance_status='breach',
                user_id='test_user'
            )
            db.session.add(covenant)
            db.session.commit()
            
            # Test GPT analysis endpoint
            response = self.client.post(f'/api/alerts/analyze/{covenant.id}')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertIn('analysis', data)
            self.assertIn('severity', data['analysis'])
            
    def test_alert_generation(self):
        """Test automatic alert generation"""
        with self.app.app_context():
            # Create test covenant in breach
            covenant = Covenant(
                name='Interest Coverage Ratio',
                description='Maintain interest coverage ratio above 2.0',
                threshold_value=2.0,
                current_value=1.8,
                compliance_status='breach',
                user_id='test_user'
            )
            db.session.add(covenant)
            db.session.commit()
            
            # Verify alert was created
            alert = Alert.query.filter_by(covenant_id=covenant.id).first()
            self.assertIsNotNone(alert)
            self.assertEqual(alert.alert_type, 'breach')
            
    def test_dashboard_data(self):
        """Test dashboard data endpoints"""
        with self.app.app_context():
            # Create test data
            covenant1 = Covenant(
                name='Current Ratio',
                description='Maintain current ratio above 1.5',
                threshold_value=1.5,
                current_value=1.6,
                compliance_status='compliant',
                user_id='test_user'
            )
            covenant2 = Covenant(
                name='Debt Service Coverage',
                description='Maintain DSCR above 1.2',
                threshold_value=1.2,
                current_value=1.1,
                compliance_status='warning',
                user_id='test_user'
            )
            db.session.add_all([covenant1, covenant2])
            db.session.commit()
            
            # Test summary endpoint
            response = self.client.get('/api/dashboard/summary')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertIn('summary', data)
            self.assertEqual(data['summary']['total'], 2)
            
    def test_document_parser(self):
        """Test GPT-powered document parser"""
        doc_path = 'loan-agreement.pdf'
        parser = DocumentParser(doc_path)
        
        # Test text extraction
        text = parser.extract_text()
        self.assertTrue(len(text) > 0)
        
        # Test covenant identification
        results = parser.process_document()
        self.assertIn('covenants', results)
        self.assertTrue(len(results['covenants']) > 0)
        
if __name__ == '__main__':
    unittest.main()
