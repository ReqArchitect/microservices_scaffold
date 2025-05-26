from common_utils.base_model import BaseModelMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Node(BaseModelMixin, db.Model):
    __tablename__ = 'nodes'
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

class Device(BaseModelMixin, db.Model):
    __tablename__ = 'devices'
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(100))

class SystemSoftware(BaseModelMixin, db.Model):
    __tablename__ = 'system_software'
    name = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(50))

class TechnologyService(BaseModelMixin, db.Model):
    __tablename__ = 'technology_services'
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

class TechnologyInterface(BaseModelMixin, db.Model):
    __tablename__ = 'technology_interfaces'
    name = db.Column(db.String(255), nullable=False)
    protocol = db.Column(db.String(100))

class TechnologyFunction(BaseModelMixin, db.Model):
    __tablename__ = 'technology_functions'
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

class TechnologyProcess(BaseModelMixin, db.Model):
    __tablename__ = 'technology_processes'
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

class TechnologyInteraction(BaseModelMixin, db.Model):
    __tablename__ = 'technology_interactions'
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

class TechnologyCollaboration(BaseModelMixin, db.Model):
    __tablename__ = 'technology_collaborations'
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

class Artifact(BaseModelMixin, db.Model):
    __tablename__ = 'artifacts'
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(100))

class Equipment(BaseModelMixin, db.Model):
    __tablename__ = 'equipment'
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(100))

class Material(BaseModelMixin, db.Model):
    __tablename__ = 'materials'
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(100))

class Facility(BaseModelMixin, db.Model):
    __tablename__ = 'facilities'
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))

class CommunicationPath(BaseModelMixin, db.Model):
    __tablename__ = 'communication_paths'
    name = db.Column(db.String(255), nullable=False)
    protocol = db.Column(db.String(100))

class DistributionNetwork(BaseModelMixin, db.Model):
    __tablename__ = 'distribution_networks'
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text) 