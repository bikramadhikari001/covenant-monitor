import os
import cloudinary
import cloudinary.uploader
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_cloudinary_upload():
    # Configure Cloudinary
    cloudinary.config( 
        cloud_name = "dhynqvbzt", 
        api_key = "346739971683127", 
        api_secret = "ZbFLtzXDj8r2_dLoCv6BRnW1E6E",
        secure = True
    )
    
    # Test file path
    file_path = Path(__file__).parent.parent / 'loan-agreement.pdf'
    
    logger.info(f"File path: {file_path}")
    logger.info(f"File exists: {file_path.exists()}")
    logger.info(f"File size: {file_path.stat().st_size} bytes")
    
    try:
        # Upload the file
        logger.info("Attempting to upload file to Cloudinary...")
        result = cloudinary.uploader.upload(
            str(file_path),
            folder="covenant-monitor/documents/test",
            resource_type="raw",
            allowed_formats=["pdf", "doc", "docx"]
        )
        
        logger.info("Upload successful!")
        logger.info(f"Secure URL: {result['secure_url']}")
        logger.info(f"Public ID: {result['public_id']}")
        logger.info(f"Full result: {result}")
        
    except Exception as e:
        logger.error(f"Error during upload: {str(e)}", exc_info=True)

if __name__ == '__main__':
    test_cloudinary_upload()
