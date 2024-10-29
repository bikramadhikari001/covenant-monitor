from flask import Blueprint, render_template, jsonify, request, session
from src.models.database import Alert, Covenant, db
from src.auth import requires_auth
from datetime import datetime, timedelta
import logging
import openai
import json
import os
from typing import Dict

logger = logging.getLogger(__name__)
alert_bp = Blueprint('alert_bp', __name__)

class AlertAnalyzer:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')

    def analyze_breach(self, covenant: Covenant) -> Dict:
        """Use GPT to analyze covenant breach and suggest actions."""
        prompt = f"""
        Analyze this covenant breach:
        
        Covenant Type: {covenant.name}
        Current Value: {covenant.current_value}
        Threshold Value: {covenant.threshold_value}
        Description: {covenant.description}
        
        Provide:
        1. Severity assessment
        2. Potential business impact
        3. Recommended actions
        4. Timeline for resolution
        
        Return as JSON with these keys:
        - severity (high/medium/low)
        - impact (description)
        - recommendations (list)
        - timeline (suggested days for resolution)
        """

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial risk analyst specializing in covenant compliance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error in GPT analysis: {str(e)}")
            return None

@alert_bp.route('/alerts')
@requires_auth
def alerts():
    user_id = session['user'].get('sub')
    active_alerts = Alert.query.filter_by(
        user_id=user_id,
        status='new'
    ).order_by(Alert.created_at.desc()).all()
    
    return render_template('alerts.html', alerts=active_alerts)

@alert_bp.route('/api/alerts/analyze/<int:covenant_id>', methods=['POST'])
@requires_auth
def analyze_alert(covenant_id):
    """Analyze a covenant breach using GPT."""
    covenant = Covenant.query.get_or_404(covenant_id)
    
    try:
        analyzer = AlertAnalyzer()
        analysis = analyzer.analyze_breach(covenant)
        
        if analysis:
            # Create or update alert with analysis
            alert = Alert.query.filter_by(
                covenant_id=covenant_id,
                status='new'
            ).first()
            
            if not alert:
                alert = Alert(
                    covenant_id=covenant_id,
                    user_id=covenant.user_id,
                    alert_type=covenant.compliance_status,
                    message=f"Covenant breach detected for {covenant.name}"
                )
            
            if alert.details:
                details = alert.details.copy()
                details['analysis'] = analysis
            else:
                details = {'analysis': analysis}
            
            alert.details = details
            db.session.add(alert)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'analysis': analysis
            })
        
        return jsonify({
            'status': 'error',
            'message': 'Could not analyze covenant breach'
        }), 500
        
    except Exception as e:
        logger.error(f"Error analyzing alert: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@alert_bp.route('/api/alerts/dismiss/<int:alert_id>', methods=['POST'])
@requires_auth
def dismiss_alert(alert_id):
    """Dismiss an alert."""
    alert = Alert.query.get_or_404(alert_id)
    
    try:
        resolution_notes = request.json.get('notes', '')
        alert.status = 'resolved'
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Alert dismissed successfully'
        })
        
    except Exception as e:
        logger.error(f"Error dismissing alert: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@alert_bp.route('/api/alerts/summary')
@requires_auth
def alert_summary():
    """Get summary of alerts by type and status."""
    user_id = session['user'].get('sub')
    
    try:
        # Get counts by type
        type_counts = db.session.query(
            Alert.alert_type,
            db.func.count(Alert.id)
        ).filter_by(
            user_id=user_id,
            status='new'
        ).group_by(Alert.alert_type).all()
        
        # Get recent alert history
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        history = db.session.query(
            db.func.date(Alert.created_at).label('date'),
            Alert.alert_type,
            db.func.count(Alert.id).label('count')
        ).filter(
            Alert.user_id == user_id,
            Alert.created_at >= thirty_days_ago
        ).group_by(
            db.func.date(Alert.created_at),
            Alert.alert_type
        ).all()
        
        return jsonify({
            'current': {
                alert_type: count
                for alert_type, count in type_counts
            },
            'history': [{
                'date': str(h.date),
                'type': h.alert_type,
                'count': h.count
            } for h in history]
        })
        
    except Exception as e:
        logger.error(f"Error getting alert summary: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@alert_bp.route('/api/alerts/recommendations/<int:alert_id>')
@requires_auth
def get_recommendations(alert_id):
    """Get GPT-generated recommendations for addressing an alert."""
    alert = Alert.query.get_or_404(alert_id)
    covenant = alert.covenant
    
    try:
        analyzer = AlertAnalyzer()
        analysis = analyzer.analyze_breach(covenant)
        
        if analysis:
            return jsonify({
                'status': 'success',
                'recommendations': analysis['recommendations'],
                'timeline': analysis['timeline']
            })
            
        return jsonify({
            'status': 'error',
            'message': 'Could not generate recommendations'
        }), 500
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
