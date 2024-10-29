"""Document routes module."""
from flask import Blueprint, request, jsonify, render_template, current_app, redirect, url_for, session
from werkzeug.utils import secure_filename
from src.models.database import db, Document, Project, Covenant
from src.document_processor.processor import DocumentProcessor
from src.auth import requires_auth
from datetime import datetime
import logging
import os
import cloudinary
import cloudinary.uploader
import tempfile
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

document_bp = Blueprint('document_bp', __name__)

# Configure Cloudinary
cloudinary.config( 
    cloud_name = "dhynqvbzt", 
    api_key = "346739971683127", 
    api_secret = "ZbFLtzXDj8r2_dLoCv6BRnW1E6E",
    secure = True
)

def allowed_file(filename):
    """Check if file type is allowed"""
    logger.debug(f"Checking if file {filename} is allowed")
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_dir():
    """Ensure upload directory exists"""
    upload_dir = os.path.join(current_app.root_path, 'uploads')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    return upload_dir

@document_bp.route('/upload', methods=['GET', 'POST'])
@requires_auth
def upload():
    """Handle document upload"""
    if request.method == 'GET':
        project_id = request.args.get('project_id')
        if not project_id:
            return jsonify({'error': 'Missing project_id'}), 400
        project = Project.query.get_or_404(project_id)
        return render_template('upload.html', project=project)

    logger.info("Processing document upload request")
    logger.debug(f"Request method: {request.method}")
    logger.debug(f"Request files: {request.files}")
    logger.debug(f"Request form: {request.form}")
    logger.debug(f"Request headers: {request.headers}")
    
    try:
        if 'file' not in request.files:
            logger.warning("No file part in request")
            logger.debug(f"Available files: {list(request.files.keys())}")
            return redirect(url_for('document_bp.upload', 
                                  project_id=request.form.get('project_id'),
                                  error='No file selected'))
        
        file = request.files['file']
        project_id = request.form.get('project_id')
        user_id = session['user']['sub']
        
        logger.debug(f"File: {file}")
        logger.debug(f"Project ID: {project_id}")
        logger.debug(f"User ID: {user_id}")
        
        if not project_id or not user_id:
            logger.warning("Missing project_id or user_id")
            return redirect(url_for('document_bp.upload',
                                  project_id=project_id,
                                  error='Missing project_id or user_id'))

        if file.filename == '':
            logger.warning("No selected file")
            return redirect(url_for('document_bp.upload',
                                  project_id=project_id,
                                  error='No file selected'))
        
        if not allowed_file(file.filename):
            logger.warning(f"File type not allowed: {file.filename}")
            return redirect(url_for('document_bp.upload',
                                  project_id=project_id,
                                  error='File type not allowed'))
        
        # Ensure upload directory exists
        upload_dir = ensure_upload_dir()
        
        # Save file temporarily with a unique name
        filename = secure_filename(file.filename)
        temp_path = os.path.join(upload_dir, f"{datetime.utcnow().timestamp()}_{filename}")
        logger.debug(f"Saving file temporarily to: {temp_path}")
        file.save(temp_path)
        
        try:
            # Upload to Cloudinary
            logger.info("Uploading file to Cloudinary")
            result = cloudinary.uploader.upload(
                temp_path,
                folder=f"covenant-monitor/documents/{project_id}",
                resource_type="raw",
                allowed_formats=["pdf", "doc", "docx"]
            )
            logger.debug(f"Cloudinary upload result: {result}")
            
            # Process document
            logger.info("Processing document")
            processor = DocumentProcessor(temp_path, user_id, project_id)
            processor.file_url = result['secure_url']  # Pass the file URL to the processor
            document = processor.process_and_store()
            
            logger.info("Document processed successfully")
            # Redirect to process page instead of project detail
            return redirect(url_for('document_bp.process', document_id=document.id))
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}", exc_info=True)
        return redirect(url_for('document_bp.upload',
                              project_id=project_id,
                              error='Failed to upload document'))

@document_bp.route('/process/<int:document_id>')
@requires_auth
def process(document_id):
    """Display document processing page"""
    document = Document.query.get_or_404(document_id)
    return render_template('process.html', document=document)

@document_bp.route('/projects', methods=['GET', 'POST'])
@requires_auth
def projects():
    """Handle project creation and listing"""
    user_id = session['user']['sub']
    logger.debug(f"User ID from session: {user_id}")
    
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')

            if not name:
                return jsonify({'error': 'Missing required fields'}), 400

            project = Project(
                name=name,
                description=description,
                user_id=user_id,
                created_at=datetime.utcnow()
            )
            db.session.add(project)
            db.session.commit()

            return redirect(url_for('document_bp.project_detail', project_id=project.id))

        except Exception as e:
            logger.error(f"Error creating project: {str(e)}", exc_info=True)
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    # Only show projects belonging to the logged-in user
    projects = Project.query.filter_by(user_id=user_id).all()
    return render_template('projects.html', projects=projects)

@document_bp.route('/project/<int:project_id>')
@requires_auth
def project_detail(project_id):
    """Display project details"""
    project = Project.query.get_or_404(project_id)
    
    # Get document count
    document_count = Document.query.filter_by(project_id=project_id).count()
    
    # Get covenant count
    covenant_count = db.session.query(Covenant).join(Document).filter(Document.project_id == project_id).count()
    
    logger.debug(f"Found {document_count} documents and {covenant_count} covenants for project {project_id}")
    
    return render_template('project_detail.html', 
                         project=project,
                         document_count=document_count,
                         covenant_count=covenant_count)

@document_bp.route('/project/<int:project_id>/delete', methods=['POST'])
@requires_auth
def delete_project(project_id):
    """Delete a project"""
    try:
        project = Project.query.get_or_404(project_id)
        
        # Delete associated documents first
        Document.query.filter_by(project_id=project_id).delete()
        db.session.commit()
        
        # Now delete the project
        db.session.delete(project)
        db.session.commit()
        
        return redirect(url_for('dashboard_bp.dashboard'))
    except Exception as e:
        logger.error(f"Error deleting project: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@document_bp.route('/project/<int:project_id>/configure-database', methods=['POST'])
@requires_auth
def configure_database(project_id):
    """Configure database connection for a project"""
    try:
        project = Project.query.get_or_404(project_id)
        # For now, just redirect back to project detail
        return redirect(url_for('document_bp.project_detail', project_id=project_id))
    except Exception as e:
        logger.error(f"Error configuring database: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500
