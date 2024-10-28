import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from src.models.database import db, Document
from src.document_processor.processor import DocumentProcessor
import cloudinary
import cloudinary.uploader
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.info("Initializing document blueprint")

document_bp = Blueprint('document_bp', __name__)
logger.info("Document blueprint created")

try:
    # Configure Cloudinary
    logger.info("Configuring Cloudinary")
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET')
    )
    logger.info("Cloudinary configured successfully")
except Exception as e:
    logger.error(f"Error configuring Cloudinary: {str(e)}", exc_info=True)

def allowed_file(filename):
    """Check if file type is allowed"""
    logger.debug(f"Checking if file {filename} is allowed")
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file_to_cloudinary(file, folder):
    """Upload file to Cloudinary"""
    logger.info(f"Attempting to upload file to Cloudinary in folder: {folder}")
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="raw",
            allowed_formats=["pdf", "doc", "docx"]
        )
        logger.info("File uploaded successfully to Cloudinary")
        return result['secure_url']
    except Exception as e:
        logger.error(f"Error uploading to Cloudinary: {str(e)}", exc_info=True)
        return None

@document_bp.route('/upload', methods=['POST'])
def upload():
    """Handle document upload"""
    logger.info("Processing document upload request")
    try:
        if 'file' not in request.files:
            logger.warning("No file part in request")
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.warning("No selected file")
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            logger.warning(f"File type not allowed: {file.filename}")
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Get project and user IDs
        project_id = request.form.get('project_id')
        user_id = request.form.get('user_id')
        
        if not project_id or not user_id:
            logger.warning("Missing project_id or user_id")
            return jsonify({'error': 'Missing project_id or user_id'}), 400
        
        # Upload to Cloudinary
        logger.info("Uploading file to Cloudinary")
        folder = f"covenant-monitor/documents/{project_id}"
        file_url = upload_file_to_cloudinary(file, folder)
        
        if not file_url:
            logger.error("Failed to upload file to Cloudinary")
            return jsonify({'error': 'Failed to upload file'}), 500
        
        # Process document
        logger.info("Processing document")
        processor = DocumentProcessor(file_url, user_id, project_id)
        document = processor.process_and_store()
        
        logger.info("Document processed successfully")
        return jsonify({
            'message': 'Document uploaded and processed successfully',
            'document_id': document.id,
            'file_url': file_url
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

logger.info("Document routes initialized successfully")
