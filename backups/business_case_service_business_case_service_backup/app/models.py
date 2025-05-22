# DB models

from .extensions import db

class BusinessCase(db.Model):
    __tablename__ = 'business_cases'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)  # FK to user service
    tenant_id = db.Column(db.Integer, nullable=False, index=True)  # FK to tenant
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    justification = db.Column(db.Text)
    expected_benefits = db.Column(db.Text)
    risk_assessment = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tenant_id': self.tenant_id,
            'title': self.title,
            'description': self.description,
            'justification': self.justification,
            'expected_benefits': self.expected_benefits,
            'risk_assessment': self.risk_assessment,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
