from .models import Report, db

class ReportService:
    @staticmethod
    def create_report(data):
        report = Report(**data)
        db.session.add(report)
        db.session.commit()
        return report

    @staticmethod
    def get_report(report_id):
        return Report.query.get(report_id)

    @staticmethod
    def get_reports(limit=10, offset=0):
        return Report.query.order_by(Report.created_at.desc()).limit(limit).offset(offset).all() 