from common_utils.base_model import BaseModelMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class ImplementationProject(BaseModelMixin, db.Model):
    __tablename__ = 'implementation_projects'
    project_id = db.Column(db.String(64), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    milestones = db.Column(db.JSON)  # List of milestones with name and dueDate
    work_packages = db.relationship('WorkPackage', backref='project', lazy=True)

class WorkPackage(BaseModelMixin, db.Model):
    __tablename__ = 'work_packages'
    work_package_id = db.Column(db.String(64), unique=True, nullable=True)
    project_id = db.Column(db.String(64), db.ForeignKey('implementation_projects.project_id'))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(64))
    assigned_team = db.Column(db.String(128))
    expected_completion_date = db.Column(db.Date)
    deliverables = db.relationship('Deliverable', backref='work_package', lazy=True)
    events = db.relationship('ImplementationEvent', backref='work_package', lazy=True)
    gaps = db.relationship('Gap', backref='work_package', lazy=True)

class Deliverable(BaseModelMixin, db.Model):
    __tablename__ = 'deliverables'
    deliverable_id = db.Column(db.String(64), unique=True, nullable=True)
    work_package_id = db.Column(db.String(64), db.ForeignKey('work_packages.work_package_id'))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(64))
    file_link = db.Column(db.String(512))

class ImplementationEvent(BaseModelMixin, db.Model):
    __tablename__ = 'implementation_events'
    event_id = db.Column(db.String(64), unique=True, nullable=True)
    work_package_id = db.Column(db.String(64), db.ForeignKey('work_packages.work_package_id'))
    name = db.Column(db.String(255), nullable=False)
    event_type = db.Column(db.String(64))
    event_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)

class Gap(BaseModelMixin, db.Model):
    __tablename__ = 'gaps'
    gap_id = db.Column(db.String(64), unique=True, nullable=True)
    work_package_id = db.Column(db.String(64), db.ForeignKey('work_packages.work_package_id'))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    impact = db.Column(db.String(64))
    suggested_resolution = db.Column(db.Text)

class Plateau(BaseModelMixin, db.Model):
    __tablename__ = 'plateaus'
    plateau_id = db.Column(db.String(64), unique=True, nullable=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    phase = db.Column(db.String(64))
    architecture_summary = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)