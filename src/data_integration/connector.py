import sqlite3
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime, timedelta
import logging
from src.models.database import Covenant, Alert, db
import openai
import json
import os

logger = logging.getLogger(__name__)

class DatabaseConnector:
    def __init__(self, db_path: str):
        self.db_path = db_path
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4')
    
    def connect(self):
        """Create a database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {str(e)}")
            raise
    
    def fetch_financial_metrics(self, metric_names: List[str]) -> Dict[str, float]:
        """Fetch current financial metrics from client database"""
        conn = self.connect()
        metrics = {}
        
        try:
            for metric in metric_names:
                query = """
                    SELECT value 
                    FROM financial_metrics 
                    WHERE metric_name = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """
                cursor = conn.execute(query, (metric,))
                result = cursor.fetchone()
                if result:
                    metrics[metric] = result[0]
        finally:
            conn.close()
        
        return metrics
    
    def fetch_historical_data(self, metric_name: str, start_date: datetime, 
                            end_date: datetime) -> pd.DataFrame:
        """Fetch historical data for a specific metric"""
        conn = self.connect()
        
        try:
            query = """
                SELECT timestamp, value 
                FROM financial_metrics 
                WHERE metric_name = ? 
                AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp
            """
            
            df = pd.read_sql_query(
                query, 
                conn, 
                params=(metric_name, start_date, end_date),
                parse_dates=['timestamp']
            )
            
            return df
        finally:
            conn.close()

    def analyze_metric_calculation(self, covenant_description: str) -> Dict[str, Any]:
        """Use GPT to analyze how to calculate a metric from available data."""
        prompt = f"""
        Given this covenant requirement:
        "{covenant_description}"
        
        Determine:
        1. What financial metrics are needed to calculate this covenant
        2. The exact calculation formula
        3. The SQL query needed to fetch the required data
        
        Return as a JSON object with these keys:
        - required_metrics: list of metric names
        - calculation_formula: string describing the calculation
        - sql_query: SQL query to fetch needed data
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial analyst who understands covenant calculations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error in GPT analysis: {str(e)}")
            return None

class DataIntegrator:
    def __init__(self, client_db_path: str):
        self.client_connector = DatabaseConnector(client_db_path)
    
    def update_covenant_values(self, covenants: List[Covenant]):
        """Update covenant values based on latest financial metrics"""
        for covenant in covenants:
            try:
                # Get calculation details using GPT
                calculation = self.client_connector.analyze_metric_calculation(
                    covenant.description
                )
                
                if not calculation:
                    continue
                
                # Fetch required metrics
                metrics = self.client_connector.fetch_financial_metrics(
                    calculation['required_metrics']
                )
                
                # Calculate new value
                new_value = self.calculate_covenant_value(metrics, calculation)
                if new_value is not None:
                    # Update covenant
                    covenant.current_value = new_value
                    covenant.last_updated = datetime.utcnow()
                    covenant.update_compliance_status()
                    
                    # Log the update
                    logger.info(f"Updated covenant {covenant.id}: {new_value}")
                
            except Exception as e:
                logger.error(f"Error updating covenant {covenant.id}: {str(e)}")
                continue
        
        # Commit all updates
        try:
            db.session.commit()
        except Exception as e:
            logger.error(f"Error committing updates: {str(e)}")
            db.session.rollback()
    
    def calculate_covenant_value(self, metrics: Dict[str, float], 
                               calculation: Dict[str, Any]) -> float:
        """Calculate covenant value from metrics using the specified formula."""
        try:
            # Create a namespace for eval
            namespace = metrics.copy()
            
            # Extract the formula
            formula = calculation['calculation_formula']
            
            # Evaluate the formula
            result = eval(formula, {"__builtins__": {}}, namespace)
            return float(result)
            
        except Exception as e:
            logger.error(f"Error calculating covenant value: {str(e)}")
            return None
    
    def get_historical_trends(self, covenant: Covenant, days: int = 90) -> pd.DataFrame:
        """Get historical trend data for a covenant"""
        try:
            # Get calculation details
            calculation = self.client_connector.analyze_metric_calculation(
                covenant.description
            )
            
            if not calculation:
                return pd.DataFrame()
            
            # Set date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Fetch historical data for each required metric
            metric_data = {}
            for metric in calculation['required_metrics']:
                df = self.client_connector.fetch_historical_data(
                    metric, start_date, end_date
                )
                metric_data[metric] = df
            
            # Combine and calculate historical values
            # This would need to be customized based on the specific calculation
            return self.combine_historical_data(metric_data, calculation)
            
        except Exception as e:
            logger.error(f"Error getting historical trends: {str(e)}")
            return pd.DataFrame()
    
    def combine_historical_data(self, metric_data: Dict[str, pd.DataFrame], 
                              calculation: Dict[str, Any]) -> pd.DataFrame:
        """Combine historical metric data into covenant values."""
        # Implementation would depend on specific calculation requirements
        # This is a placeholder for custom logic
        return pd.DataFrame()

def setup_data_integration(app):
    """Setup data integration with periodic updates"""
    integrator = DataIntegrator('path_to_client_db.sqlite')
    
    def update_covenant_data():
        with app.app_context():
            covenants = Covenant.query.all()
            integrator.update_covenant_values(covenants)
    
    # Schedule periodic updates
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_covenant_data, 'interval', minutes=15)
    scheduler.start()
    
    return integrator
