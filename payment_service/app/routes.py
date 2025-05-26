from flask import Blueprint, request, jsonify
from .service import PaymentService, SubscriptionService
from .schemas import PaymentSchema, SubscriptionSchema
from flasgger import swag_from
from datetime import datetime

payment_bp = Blueprint('payment', __name__, url_prefix='/api/v1/payment')

# Payment endpoints
@payment_bp.route('/payments', methods=['POST'])
@swag_from({"summary": "Create payment", "responses": {201: {"description": "Created"}}})
def create_payment():
    data = request.get_json()
    payment = PaymentService.create_payment(data)
    return PaymentSchema().jsonify(payment), 201

@payment_bp.route('/payments/<int:payment_id>', methods=['GET'])
@swag_from({"summary": "Get payment", "responses": {200: {"description": "OK"}, 404: {"description": "Not found"}}})
def get_payment(payment_id):
    payment = PaymentService.get_payment(payment_id)
    if not payment:
        return jsonify({'message': 'Not found'}), 404
    return PaymentSchema().jsonify(payment)

@payment_bp.route('/payments', methods=['GET'])
@swag_from({"summary": "List payments", "responses": {200: {"description": "OK"}}})
def get_payments():
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    payments = PaymentService.get_payments(limit, offset)
    return PaymentSchema(many=True).jsonify(payments)

# Subscription endpoints
@payment_bp.route('/subscriptions', methods=['POST'])
@swag_from({"summary": "Create subscription", "responses": {201: {"description": "Created"}}})
def create_subscription():
    data = request.get_json()
    sub = SubscriptionService.create_subscription(data)
    return SubscriptionSchema().jsonify(sub), 201

@payment_bp.route('/subscriptions/<int:sub_id>', methods=['GET'])
@swag_from({"summary": "Get subscription", "responses": {200: {"description": "OK"}, 404: {"description": "Not found"}}})
def get_subscription(sub_id):
    sub = SubscriptionService.get_subscription(sub_id)
    if not sub:
        return jsonify({'message': 'Not found'}), 404
    return SubscriptionSchema().jsonify(sub)

@payment_bp.route('/subscriptions', methods=['GET'])
@swag_from({"summary": "List subscriptions", "responses": {200: {"description": "OK"}}})
def get_subscriptions():
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    subs = SubscriptionService.get_subscriptions(limit, offset)
    return SubscriptionSchema(many=True).jsonify(subs)

@payment_bp.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "payment-service", "timestamp": datetime.utcnow().isoformat()})

@payment_bp.route('/metrics', methods=['GET'])
def metrics():
    # Dummy metrics
    return jsonify({"total_payments": len(PaymentService.get_payments(1000, 0)), "total_subscriptions": len(SubscriptionService.get_subscriptions(1000, 0))}) 