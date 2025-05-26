from flask import Blueprint, request, jsonify
from .models import db, Notification, NotificationTemplate, Subscription, UserNotificationLog

bp = Blueprint('notifications', __name__)

# POST /notifications
@bp.route('/notifications', methods=['POST'])
def create_notification():
    data = request.json
    # Validate and create notification (stubbed delivery)
    notification = Notification(
        user_id=data['userId'],
        channel=data['channel'],
        template_id=data['templateId'],
        payload=data['payload'],
        subscription_id=None
    )
    db.session.add(notification)
    db.session.commit()
    # Log delivery (stub)
    log = UserNotificationLog(
        user_id=data['userId'],
        notification_id=notification.id,
        channel=data['channel'],
        status='SENT',
        response_code='200'
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({'id': notification.id, 'status': 'queued'}), 201

# PUT /subscriptions/{userId}
@bp.route('/subscriptions/<user_id>', methods=['PUT'])
def update_subscription(user_id):
    data = request.json
    sub = Subscription.query.filter_by(user_id=user_id).first()
    if not sub:
        sub = Subscription(user_id=user_id)
        db.session.add(sub)
    sub.email = data.get('email', sub.email)
    sub.sms = data.get('sms', sub.sms)
    sub.push = data.get('push', sub.push)
    sub.in_app = data.get('inApp', sub.in_app)
    db.session.commit()
    return jsonify({'userId': user_id, 'preferences': data}), 200

# GET /subscriptions/{userId}
@bp.route('/subscriptions/<user_id>', methods=['GET'])
def get_subscription(user_id):
    sub = Subscription.query.filter_by(user_id=user_id).first()
    if not sub:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({
        'userId': sub.user_id,
        'email': sub.email,
        'sms': sub.sms,
        'push': sub.push,
        'inApp': sub.in_app
    })

# POST /notification-templates
@bp.route('/notification-templates', methods=['POST'])
def create_template():
    data = request.json
    template = NotificationTemplate(
        template_id=data['templateId'],
        channel=data['channel'],
        subject=data.get('subject'),
        body=data.get('body')
    )
    db.session.add(template)
    db.session.commit()
    return jsonify({'id': template.id}), 201

# PUT /notification-templates/{templateId}
@bp.route('/notification-templates/<template_id>', methods=['PUT'])
def update_template(template_id):
    data = request.json
    template = NotificationTemplate.query.filter_by(template_id=template_id).first()
    if not template:
        return jsonify({'error': 'Not found'}), 404
    template.subject = data.get('subject', template.subject)
    template.body = data.get('body', template.body)
    db.session.commit()
    return jsonify({'id': template.id}), 200

# GET /notification-templates/{templateId}
@bp.route('/notification-templates/<template_id>', methods=['GET'])
def get_template(template_id):
    template = NotificationTemplate.query.filter_by(template_id=template_id).first()
    if not template:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({
        'templateId': template.template_id,
        'channel': template.channel,
        'subject': template.subject,
        'body': template.body
    })

# GET /notification-templates
@bp.route('/notification-templates', methods=['GET'])
def list_templates():
    templates = NotificationTemplate.query.all()
    return jsonify([
        {
            'templateId': t.template_id,
            'channel': t.channel,
            'subject': t.subject,
            'body': t.body
        } for t in templates
    ])

# GET /user-notifications/{userId}
@bp.route('/user-notifications/<user_id>', methods=['GET'])
def get_user_notifications(user_id):
    logs = UserNotificationLog.query.filter_by(user_id=user_id).all()
    return jsonify([
        {
            'notificationId': l.notification_id,
            'channel': l.channel,
            'status': l.status,
            'responseCode': l.response_code,
            'sentAt': l.sent_at.isoformat()
        } for l in logs
    ])
