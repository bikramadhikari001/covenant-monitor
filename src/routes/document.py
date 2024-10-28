import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from src.models.database import db, Document
from src.document_processor.processor import DocumentProcessor
import cloudinary
import cloudinary.uploader
import logging

document_bp = Blueprint('document_bp', __name__)
logger = logging.getLogger(__name__)

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

def allowed_file(filename):
    """Check if file type is allowed"""
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file_to_cloudinary(file, folder):
    """Upload file to Cloudinary"""
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="raw",
            allowed_formats=["pdf", "doc", "docx"]
        )
        return result['secure_url']
    except Exception as e:
        logger.error(f"Error uploading to Cloudinary: {str(e)}")
        return None

@document_bp.route('/upload', methods=['POST'])
def upload():
    """Handle document upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Get project and user IDs
        project_id = request.form.get('project_id')
        user_id = request.form.get('user_id')
        
        if not project_id or not user_id:
            return jsonify({'error': 'Missing project_id or user_id'}), 400
        
        # Upload to Cloudinary
        folder = f"covenant-monitor/documents/{project_id}"
        file_url = upload_file_to_cloudinary(file, folder)
        
        if not file_url:
            return jsonify({'error': 'Failed to upload file'}), 500
        
        # Process document
        processor = DocumentProcessor(file_url, user_id, project_id)
        document = processor.process_and_store()
        
        return jsonify({
            'message': 'Document uploaded and processed successfully',
            'document_id': document.id,
            'file_url': file_url
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@document_bp.route('/<int:document_id>', methods=['GET'])
def get_document(document_id):
    """Get document details"""
    document = Document.query.get_or_404(document_id)
    
    return jsonify({
        'id': document.id,
        'filename': document.filename,
        'upload_date': document.upload_date.isoformat(),
        'document_type': document.document_type,
        'processing_status': document.processing_status,
        'file_url': document.file_url
    })

@document_bp.route('/<int:document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete document"""
    document = Document.query.get_or_404(document_id)
    
    # Delete from Cloudinary if URL exists
    if document.file_url:
        try:
            # Extract public_id from URL
            public_id = document.file_url.split('/')[-1].split('.')[0]
            cloudinary.uploader.destroy(public_id)
        except Exception as e:
            logger.error(f"Error deleting from Cloudinary: {str(e)}")
    
    # Delete from database
    db.session.delete(document)
    db.session.commit()
    
    return jsonify({'message': 'Document deleted successfully'})
