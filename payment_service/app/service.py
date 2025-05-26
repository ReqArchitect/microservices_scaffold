from .models import Payment, Subscription, db

class PaymentService:
    @staticmethod
    def create_payment(data):
        payment = Payment(**data)
        db.session.add(payment)
        db.session.commit()
        return payment

    @staticmethod
    def get_payment(payment_id):
        return Payment.query.get(payment_id)

    @staticmethod
    def get_payments(limit=10, offset=0):
        return Payment.query.order_by(Payment.created_at.desc()).limit(limit).offset(offset).all()

class SubscriptionService:
    @staticmethod
    def create_subscription(data):
        sub = Subscription(**data)
        db.session.add(sub)
        db.session.commit()
        return sub

    @staticmethod
    def get_subscription(sub_id):
        return Subscription.query.get(sub_id)

    @staticmethod
    def get_subscriptions(limit=10, offset=0):
        return Subscription.query.order_by(Subscription.started_at.desc()).limit(limit).offset(offset).all() 