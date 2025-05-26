from common_utils.base_model import BaseModelMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Driver(BaseModelMixin, db.Model):
    __tablename__ = 'drivers'
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

class Assessment(BaseModelMixin, db.Model):
    __tablename__ = 'assessments'
    name = db.Column(db.String(255), nullable=False)
    result = db.Column(db.Text)

class Goal(BaseModelMixin, db.Model):
    __tablename__ = 'goals'
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

class Objective(BaseModelMixin, db.Model):
    __tablename__ = 'objectives'
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

class Requirement(BaseModelMixin, db.Model):
    __tablename__ = 'requirements'
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

class Constraint(BaseModelMixin, db.Model):
    __tablename__ = 'constraints'
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

class Principle(BaseModelMixin, db.Model):
    __tablename__ = 'principles'
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

class Outcome(BaseModelMixin, db.Model):
    __tablename__ = 'outcomes'
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

class Stakeholder(BaseModelMixin, db.Model):
    __tablename__ = 'stakeholders'
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(100))

class Meaning(BaseModelMixin, db.Model):
    __tablename__ = 'meanings'
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

class Value(BaseModelMixin, db.Model):
    __tablename__ = 'values'
    name = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float) 