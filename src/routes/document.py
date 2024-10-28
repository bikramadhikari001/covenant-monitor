"""Document routes."""
from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
from src.auth import requires_auth
from src.document_processor.processor import DocumentProcessor
from src.models.database import db, Document, Project, Covenant
import os
import logging

logger = logging.getLogger(__name__)
document_bp = Blueprint('document_bp', __name__)

def get_user_id():
    """Get user ID from session."""
    if 'user' not in session:
        return 'default'
    return session['user'].get('userinfo', {}).get('email', 'default')

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@document_bp.route('/upload', methods=['GET', 'POST'])
@requires_auth
def upload():
    """Handle document upload."""
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        # Get project information
        project_id = request.form.get('project_id')
        if not project_id:
            flash('Please select a project', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                # Save the uploaded file
                filename = secure_filename(file.filename)
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                
                # Process the document
                user_id = get_user_id()
                processor = DocumentProcessor(file_path, user_id, project_id=int(project_id))
                document = processor.process_and_store()
                
                flash('Document uploaded and processed successfully', 'success')
                return redirect(url_for('document_bp.process', document_id=document.id))
                
            except Exception as e:
                logger.error(f"Error processing document: {str(e)}", exc_info=True)
                flash('Error processing document. Please try again.', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload a PDF, DOC, or DOCX file.', 'error')
            return redirect(request.url)
    
    # Get project_id from query parameter
    project_id = request.args.get('project_id')
    
    # Get list of projects for the dropdown (only if no project_id provided)
    user_id = get_user_id()
    projects = Project.query.filter_by(user_id=user_id).all() if not project_id else None
    
    return render_template('upload.html', projects=projects, project_id=project_id)

@document_bp.route('/process/<int:document_id>')
@requires_auth
def process(document_id):
    """Show document processing results."""
    document = Document.query.get_or_404(document_id)
    return render_template('process.html', document=document)

@document_bp.route('/projects', methods=['GET', 'POST'])
@requires_auth
def projects():
    """Handle project management."""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Project name is required', 'error')
            return redirect(request.url)
        
        user_id = get_user_id()
        project = Project(
            name=name,
            description=description,
            user_id=user_id
        )
        db.session.add(project)
        db.session.commit()
        
        flash('Project created successfully', 'success')
        return redirect(url_for('document_bp.project_detail', project_id=project.id))
    
    user_id = get_user_id()
    projects = Project.query.filter_by(user_id=user_id).all()
    return render_template('projects.html', projects=projects)

@document_bp.route('/project/<int:project_id>')
@requires_auth
def project_detail(project_id):
    """Show project details."""
    project = Project.query.get_or_404(project_id)
    
    # Get covenant statistics for this project
    covenants = Covenant.query.join(Document).filter(Document.project_id == project_id).all()
    compliant_count = sum(1 for c in covenants if c.compliance_status == 'compliant')
    warning_count = sum(1 for c in covenants if c.compliance_status == 'warning')
    
    return render_template('project_detail.html',
                         project=project,
                         compliant_count=compliant_count,
                         warning_count=warning_count)

@document_bp.route('/project/<int:project_id>/configure-database', methods=['POST'])
@requires_auth
def configure_database(project_id):
    """Configure database connection for a project."""
    project = Project.query.get_or_404(project_id)
    
    # Get database configuration from form
    db_type = request.form.get('db_type')
    host = request.form.get('host')
    port = request.form.get('port')
    database = request.form.get('database')
    username = request.form.get('username')
    password = request.form.get('password')
    
    try:
        # Store database configuration (in real app, encrypt sensitive data)
        project.db_config = {
            'type': db_type,
            'host': host,
            'port': port,
            'database': database,
            'username': username
            # Don't store password in plain text
        }
        db.session.commit()
        
        flash('Database configured successfully', 'success')
    except Exception as e:
        logger.error(f"Error configuring database: {str(e)}", exc_info=True)
        flash('Error configuring database', 'error')
    
    return redirect(url_for('document_bp.project_detail', project_id=project_id))

@document_bp.route('/project/<int:project_id>/delete', methods=['POST'])
@requires_auth
def delete_project(project_id):
    """Delete a project."""
    project = Project.query.get_or_404(project_id)
    
    # Verify user owns this project
    if project.user_id != get_user_id():
        flash('You do not have permission to delete this project', 'error')
        return redirect(url_for('dashboard_bp.dashboard'))
    
    try:
        db.session.delete(project)
        db.session.commit()
        flash('Project deleted successfully', 'success')
    except Exception as e:
        logger.error(f"Error deleting project: {str(e)}", exc_info=True)
        flash('Error deleting project', 'error')
    
    return redirect(url_for('dashboard_bp.dashboard'))
