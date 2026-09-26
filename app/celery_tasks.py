from celery import Celery

celery_app = Celery(
    "secure_product_api",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)


@celery_app.task
def send_notification(name: str):
    print(f"Notification sent to {name}")

    return {
        "message": f"Notification sent to {name}"
    }


@celery_app.task
def process_product(product_id: int):
    print(f"Processing product {product_id}")

    return {
        "message": f"Product {product_id} processed successfully"
    }