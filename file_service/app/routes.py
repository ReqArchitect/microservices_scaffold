from flask import Blueprint, request, jsonify, send_file
from .models import db, UploadedFile, Attachment, ExportJob, ExcelImport, ImageVerificationResult
from werkzeug.utils import secure_filename
import os

bp = Blueprint('files', __name__)
UPLOAD_FOLDER = 'uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# POST /files/upload
@bp.route('/files/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    user_id = request.form['userId']
    linked_entity = request.form['linkedEntity']
    file_type = request.form['fileType']
    description = request.form.get('description')
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    uploaded = UploadedFile(
        file_name=filename,
        file_type=file_type,
        file_size=os.path.getsize(file_path),
        storage_url=file_path,  # Replace with S3 URL in prod
        user_id=user_id,
        linked_entity=linked_entity,
        description=description
    )
    db.session.add(uploaded)
    db.session.commit()
    return jsonify({'fileId': uploaded.id, 'fileName': filename}), 201

# GET /files/<fileId>/download
@bp.route('/files/<int:file_id>/download', methods=['GET'])
def download_file(file_id):
    uploaded = UploadedFile.query.get(file_id)
    if not uploaded:
        return jsonify({'error': 'Not found'}), 404
    # TODO: Add access control
    return send_file(uploaded.storage_url, as_attachment=True)

# GET /files/metadata
@bp.route('/files/metadata', methods=['GET'])
def get_metadata():
    # Filter by query params: linkedEntity, fileType, date range
    query = UploadedFile.query
    if 'linkedEntity' in request.args:
        query = query.filter_by(linked_entity=request.args['linkedEntity'])
    if 'fileType' in request.args:
        query = query.filter_by(file_type=request.args['fileType'])
    files = query.all()
    return jsonify([
        {
            'fileId': f.id,
            'fileName': f.file_name,
            'fileType': f.file_type,
            'fileSize': f.file_size,
            'uploadDate': f.upload_date.isoformat(),
            'linkedEntity': f.linked_entity
        } for f in files
    ])

# POST /files/export
@bp.route('/files/export', methods=['POST'])
def export_data():
    data = request.json
    job = ExportJob(
        user_id=data['userId'],
        export_format=data['exportFormat'],
        data_scope=data['dataScope']
    )
    db.session.add(job)
    db.session.commit()
    # TODO: Trigger background export job
    return jsonify({'jobId': job.id, 'status': job.status}), 202

# GET /files/export-jobs/<int:job_id>
@bp.route('/files/export-jobs/<int:job_id>', methods=['GET'])
def get_export_job(job_id):
    job = ExportJob.query.get(job_id)
    if not job:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({
        'jobId': job.id,
        'status': job.status,
        'resultUrl': job.result_url
    })

# POST /files/import-excel
@bp.route('/files/import-excel', methods=['POST'])
def import_excel():
    file = request.files['file']
    user_id = request.form['userId']
    import_type = request.form['importType']
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    # TODO: Validate and parse Excel, AI verification
    excel_import = ExcelImport(
        user_id=user_id,
        import_type=import_type,
        status='COMPLETED',
        result={'message': 'Stub: Excel processed'},
        file_id=None
    )
    db.session.add(excel_import)
    db.session.commit()
    return jsonify({'importId': excel_import.id, 'status': excel_import.status}), 201

# POST /files/attachments
@bp.route('/files/attachments', methods=['POST'])
def create_attachment():
    data = request.json
    attachment = Attachment(
        attachment_type=data['attachmentType'],
        file_id=data['fileId'],
        linked_entity=data['linkedEntity']
    )
    db.session.add(attachment)
    db.session.commit()
    return jsonify({'attachmentId': attachment.id}), 201

# GET /files/attachments/<entityId>
@bp.route('/files/attachments/<entity_id>', methods=['GET'])
def get_attachments(entity_id):
    attachments = Attachment.query.filter_by(linked_entity=entity_id).all()
    return jsonify([
        {
            'attachmentId': a.id,
            'fileId': a.file_id,
            'attachmentType': a.attachment_type
        } for a in attachments
    ])

# POST /files/verify-image
@bp.route('/files/verify-image', methods=['POST'])
def verify_image():
    file = request.files['file']
    user_id = request.form['userId']
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    # TODO: AI validation stub
    result = ImageVerificationResult(
        user_id=user_id,
        file_id=None,
        passed=True,
        details={'message': 'Stub: Image verified'}
    )
    db.session.add(result)
    db.session.commit()
    return jsonify({'verificationId': result.id, 'passed': result.passed}), 201
