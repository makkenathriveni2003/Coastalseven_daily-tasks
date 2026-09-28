from app.models.product import Product
from app.models.user import User
from app.utils.security import create_access_token


def test_cart_flow_and_order_creation(db, client):
    customer = User(name="Customer", email="customer@example.com", password_hash="hash", role="customer")
    admin = User(name="Admin", email="admin@example.com", password_hash="hash", role="admin")
    db.add(customer)
    db.add(admin)
    db.commit()
    db.refresh(customer)
    db.refresh(admin)

    product = Product(name="Keyboard", description="Mechanical", price=120.0, stock=5, image_url="https://example.com/keyboard.jpg")
    db.add(product)
    db.commit()
    db.refresh(product)

    token = create_access_token(customer.email)
    client.headers.update({"Authorization": f"Bearer {token}"})

    add_response = client.post("/cart/add", json={"product_id": product.id, "quantity": 2})
    assert add_response.status_code == 201
    assert add_response.json()["items"] == [{"product_id": product.id, "quantity": 2}]

    cart_response = client.get("/cart/")
    assert cart_response.status_code == 200
    assert cart_response.json()["items"] == [{"product_id": product.id, "quantity": 2}]

    update_response = client.put("/cart/update", json={"product_id": product.id, "quantity": 3})
    assert update_response.status_code == 200
    assert update_response.json()["items"] == [{"product_id": product.id, "quantity": 3}]

    order_response = client.post("/orders/")
    assert order_response.status_code == 201
    assert order_response.json()["status"] == "pending"
    assert order_response.json()["total_price"] == 360.0
    assert order_response.json()["items"] == [{"product_id": product.id, "quantity": 3, "price": 120.0}]

    history_response = client.get("/orders/")
    assert history_response.status_code == 200
    assert history_response.json()[0]["id"] == order_response.json()["id"]
    assert history_response.json()[0]["status"] == "pending"

    db.refresh(product)
    assert product.stock == 2

    empty_cart = client.get("/cart/")
    assert empty_cart.json()["items"] == []

    with client.websocket_connect(f"/ws?token={token}") as websocket:
        admin_token = create_access_token(admin.email)
        update_response = client.patch(
            f"/orders/{order_response.json()['id']}/status",
            json={"status": "shipped"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert update_response.status_code == 200
        assert update_response.json()["status"] == "shipped"
        assert websocket.receive_json() == {
            "type": "order_status",
            "order_id": order_response.json()["id"],
            "status": "shipped",
        }
