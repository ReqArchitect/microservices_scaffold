from flask import Blueprint, request, jsonify
from .models import db, SubscriptionPlan, UserSubscription, BillingHistory, CreditUsage, Invoice

bp = Blueprint('billing', __name__)

# GET /subscription-plans
@bp.route('/subscription-plans', methods=['GET'])
def get_plans():
    plans = SubscriptionPlan.query.all()
    return jsonify([
        {
            'planId': p.plan_id,
            'name': p.name,
            'price': p.price,
            'features': p.features
        } for p in plans
    ])

# POST /subscription-plans
@bp.route('/subscription-plans', methods=['POST'])
def create_plan():
    data = request.json
    plan = SubscriptionPlan(
        plan_id=data['planId'],
        name=data['name'],
        price=data['price'],
        features=data.get('features', [])
    )
    db.session.add(plan)
    db.session.commit()
    return jsonify({'id': plan.id}), 201

# POST /user-subscriptions
@bp.route('/user-subscriptions', methods=['POST'])
def create_user_subscription():
    data = request.json
    sub = UserSubscription(
        user_id=data['userId'],
        plan_id=data['planId'],
        start_date=data.get('startDate'),
        end_date=data.get('endDate'),
        payment_method=data.get('paymentMethod')
    )
    db.session.add(sub)
    db.session.commit()
    return jsonify({'id': sub.id}), 201

# PUT /user-subscriptions/<userId>
@bp.route('/user-subscriptions/<user_id>', methods=['PUT'])
def update_user_subscription(user_id):
    data = request.json
    sub = UserSubscription.query.filter_by(user_id=user_id).first()
    if not sub:
        return jsonify({'error': 'Not found'}), 404
    sub.plan_id = data.get('planId', sub.plan_id)
    sub.payment_method = data.get('paymentMethod', sub.payment_method)
    db.session.commit()
    return jsonify({'id': sub.id}), 200

# DELETE /user-subscriptions/<userId>
@bp.route('/user-subscriptions/<user_id>', methods=['DELETE'])
def cancel_user_subscription(user_id):
    sub = UserSubscription.query.filter_by(user_id=user_id).first()
    if not sub:
        return jsonify({'error': 'Not found'}), 404
    db.session.delete(sub)
    db.session.commit()
    return jsonify({'status': 'cancelled'}), 200

# GET /billing-history/<userId>
@bp.route('/billing-history/<user_id>', methods=['GET'])
def get_billing_history(user_id):
    history = BillingHistory.query.filter_by(user_id=user_id).all()
    return jsonify([
        {
            'planId': h.plan_id,
            'transactionType': h.transaction_type,
            'amount': h.amount,
            'timestamp': h.timestamp.isoformat(),
            'status': h.status
        } for h in history
    ])

# POST /credit-usage
@bp.route('/credit-usage', methods=['POST'])
def record_credit_usage():
    data = request.json
    usage = CreditUsage(
        user_id=data['userId'],
        feature=data['feature'],
        credits_used=data['creditsUsed']
    )
    db.session.add(usage)
    db.session.commit()
    return jsonify({'id': usage.id}), 201

# POST /invoices/generate
@bp.route('/invoices/generate', methods=['POST'])
def generate_invoice():
    data = request.json
    invoice = Invoice(
        user_id=data['userId'],
        invoice_date=data.get('invoiceDate'),
        amount_due=data['amountDue'],
        status=data.get('status', 'Pending')
    )
    db.session.add(invoice)
    db.session.commit()
    return jsonify({'id': invoice.id}), 201

# GET /invoices/<userId>
@bp.route('/invoices/<user_id>', methods=['GET'])
def get_invoices(user_id):
    invoices = Invoice.query.filter_by(user_id=user_id).all()
    return jsonify([
        {
            'invoiceDate': i.invoice_date,
            'amountDue': i.amount_due,
            'status': i.status,
            'createdAt': i.created_at.isoformat()
        } for i in invoices
    ])
