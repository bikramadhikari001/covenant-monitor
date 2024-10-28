"""Database models."""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.sqlite import JSON

db = SQLAlchemy()

class Project(db.Model):
    """Project model for organizing documents."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    documents = db.relationship('Document', backref='project', lazy=True, cascade='all, delete-orphan')

class Document(db.Model):
    """Document model for storing uploaded files."""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.String(255), nullable=False)
    document_type = db.Column(db.String(50))
    doc_metadata = db.Column(JSON)
    processing_status = db.Column(db.String(50), default='pending')  # pending, processing, completed, error
    
    # Relationships
    covenants = db.relationship('Covenant', backref='document', lazy=True, cascade='all, delete-orphan')

class Covenant(db.Model):
    """Covenant model for storing financial covenants."""
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    user_id = db.Column(db.String(255), nullable=False)
    
    # Basic covenant information
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    threshold_value = db.Column(db.Float)
    current_value = db.Column(db.Float)
    compliance_status = db.Column(db.String(50))  # compliant, warning, breach
    
    # Monitoring details
    measurement_frequency = db.Column(db.String(50))  # monthly, quarterly, etc.
    next_review_date = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Calculation details
    calculation_method = db.Column(db.Text)
    data_source = db.Column(db.String(255))
    
    # Additional metadata
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    alerts = db.relationship('Alert', backref='covenant', lazy=True, cascade='all, delete-orphan')

    def update_compliance_status(self):
        """Update compliance status based on current and threshold values."""
        if self.current_value is None or self.threshold_value is None:
            self.compliance_status = 'pending'
            return

        # Calculate percentage of threshold
        percentage = (self.current_value / self.threshold_value) * 100

        # Determine status based on percentage
        if percentage >= 95:  # Within 5% of threshold
            if percentage > 100:
                self.compliance_status = 'breach'
            else:
                self.compliance_status = 'warning'
        else:
            self.compliance_status = 'compliant'

class Alert(db.Model):
    """Alert model for storing covenant alerts."""
    id = db.Column(db.Integer, primary_key=True)
    covenant_id = db.Column(db.Integer, db.ForeignKey('covenant.id'), nullable=False)
    user_id = db.Column(db.String(255), nullable=False)
    
    alert_type = db.Column(db.String(50), nullable=False)  # breach, warning, review_date
    message = db.Column(db.Text, nullable=False)
    details = db.Column(JSON)  # Additional alert details
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    resolved_at = db.Column(db.DateTime)
    resolution_notes = db.Column(db.Text)

    @classmethod
    def create_for_covenant(cls, covenant):
        """Create an alert for a covenant based on its status."""
        alert_type = covenant.compliance_status
        if alert_type not in ['warning', 'breach']:
            return None

        message = (
            f"{covenant.name} is in {alert_type} status. "
            f"Current value: {covenant.current_value}, "
            f"Threshold: {covenant.threshold_value}"
        )

        details = {
            'covenant_name': covenant.name,
            'current_value': covenant.current_value,
            'threshold_value': covenant.threshold_value,
            'measurement_frequency': covenant.measurement_frequency,
            'last_updated': covenant.last_updated.isoformat() if covenant.last_updated else None
        }

        alert = cls(
            covenant_id=covenant.id,
            user_id=covenant.user_id,
            alert_type=alert_type,
            message=message,
            details=details
        )

        db.session.add(alert)
        return alert

    def resolve(self, notes=None):
        """Mark an alert as resolved."""
        self.is_active = False
        self.resolved_at = datetime.utcnow()
        self.resolution_notes = notes
