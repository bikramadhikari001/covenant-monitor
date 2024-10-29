import os
import requests
from pathlib import Path
import mimetypes
import logging
from src.models.database import Document

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_content_type(filename):
    """Get the correct content type for a file"""
    content_type, _ = mimetypes.guess_type(filename)
    if content_type is None:
        # Default to application/octet-stream if type cannot be guessed
        content_type = 'application/octet-stream'
    return content_type

def test_file_upload():
    # Print Document model fields
    logger.info("Document model fields:")
    for column in Document.__table__.columns:
        logger.info(f"- {column.name}: {column.type}")
    
    # URL of your local server
    base_url = 'http://localhost:8080'
    
    # First login to get a session
    logger.info("\nLogging in...")
    session = requests.Session()
    login_response = session.get(f"{base_url}/login")
    logger.info(f"Login response status: {login_response.status_code}")
    
    # Test file path (using the loan-agreement.pdf in the root directory)
    file_path = Path(__file__).parent.parent / 'loan-agreement.pdf'
    
    logger.info(f"File path: {file_path}")
    logger.info(f"File exists: {file_path.exists()}")
    logger.info(f"File size: {file_path.stat().st_size} bytes")
    
    # Get content type
    content_type = get_content_type(file_path)
    logger.info(f"Content type: {content_type}")
    
    # Form data
    data = {
        'project_id': '2',
        'user_id': '1'
    }
    
    logger.info(f"Form data: {data}")
    
    try:
        # Get the upload page first
        logger.info("Getting upload page...")
        get_response = session.get(f"{base_url}/upload?project_id=2")
        logger.info(f"GET response status: {get_response.status_code}")
        logger.debug(f"GET response content: {get_response.text}")
        
        # File to upload
        with open(file_path, 'rb') as f:
            files = {
                'file': (file_path.name, f, content_type)
            }
            
            logger.info("Sending POST request...")
            logger.info(f"Files: {files}")
            
            response = session.post(f"{base_url}/upload", data=data, files=files)
            
            # Print response details
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response Headers: {dict(response.headers)}")
            
            # Try to get JSON response first
            try:
                json_response = response.json()
                logger.info(f"JSON Response: {json_response}")
            except:
                # If not JSON, get text response
                logger.debug(f"Full Response Text: {response.text}")
                logger.info(f"Text Response Preview: {response.text[:1000]}...")
            
            # Check if successful
            if response.ok:
                logger.info("Upload successful!")
            else:
                logger.error(f"Upload failed with status code {response.status_code}")
                
    except Exception as e:
        logger.error(f"Error during upload: {str(e)}", exc_info=True)

if __name__ == '__main__':
    test_file_upload()
