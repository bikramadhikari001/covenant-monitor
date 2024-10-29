"""Database models module."""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Project(db.Model):
    """Project model."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    documents = db.relationship('Document', backref='project', lazy=True)

class Document(db.Model):
    """Document model."""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.String(500), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.String(50), nullable=False)
    document_type = db.Column(db.String(50))
    doc_metadata = db.Column(db.Text)  # Store JSON as text in SQLite
    processing_status = db.Column(db.String(20), default='pending')
    covenants = db.relationship('Covenant', backref='document', lazy=True)

class Covenant(db.Model):
    """Covenant model."""
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    user_id = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    threshold_value = db.Column(db.Float)
    current_value = db.Column(db.Float)
    measurement_frequency = db.Column(db.String(20))  # e.g., 'monthly', 'quarterly', 'annually'
    compliance_status = db.Column(db.String(20), default='unknown')  # e.g., 'compliant', 'warning', 'breach'
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)
    covenant_metadata = db.Column(db.Text)  # Store JSON as text in SQLite
    alerts = db.relationship('Alert', backref='covenant', lazy=True)

    def update_compliance_status(self):
        """Update compliance status based on current and threshold values."""
        if self.current_value is None or self.threshold_value is None:
            self.compliance_status = 'unknown'
            return

        # For metrics where higher is better (e.g., coverage ratios)
        if 'coverage' in self.name.lower() or 'net worth' in self.name.lower():
            if self.current_value >= self.threshold_value:
                self.compliance_status = 'compliant'
            elif self.current_value >= self.threshold_value * 0.9:  # Within 90% of threshold
                self.compliance_status = 'warning'
            else:
                self.compliance_status = 'breach'
        # For metrics where lower is better (e.g., leverage ratios)
        else:
            if self.current_value <= self.threshold_value:
                self.compliance_status = 'compliant'
            elif self.current_value <= self.threshold_value * 1.1:  # Within 110% of threshold
                self.compliance_status = 'warning'
            else:
                self.compliance_status = 'breach'

class Alert(db.Model):
    """Alert model."""
    id = db.Column(db.Integer, primary_key=True)
    covenant_id = db.Column(db.Integer, db.ForeignKey('covenant.id'), nullable=False)
    user_id = db.Column(db.String(50), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # e.g., 'warning', 'breach'
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='new')  # e.g., 'new', 'read', 'resolved'
    details = db.Column(db.Text)  # Store JSON as text in SQLite
