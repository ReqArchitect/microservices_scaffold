from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class UploadedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String, nullable=False)
    file_type = db.Column(db.String, nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    storage_url = db.Column(db.String, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.String, nullable=False)
    linked_entity = db.Column(db.String, nullable=False)
    description = db.Column(db.String)

class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attachment_type = db.Column(db.String, nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('uploaded_file.id'))
    linked_entity = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ExportJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    export_format = db.Column(db.String, nullable=False)
    data_scope = db.Column(db.String, nullable=False)
    status = db.Column(db.String, default='PENDING')
    result_url = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

class ExcelImport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    import_type = db.Column(db.String, nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('uploaded_file.id'))
    status = db.Column(db.String, default='PENDING')
    result = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

class ImageVerificationResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('uploaded_file.id'))
    passed = db.Column(db.Boolean)
    details = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
