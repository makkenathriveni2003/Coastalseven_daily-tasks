from celery import shared_task


@shared_task
def send_order_confirmation_email(user_email: str, order_id: int):
    print(f"Sending order confirmation email to {user_email} for order {order_id}")
    return {"status": "email_sent", "user_email": user_email, "order_id": order_id}
