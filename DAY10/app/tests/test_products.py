from app.models.user import User
from app.utils.security import create_access_token


def test_admin_can_create_and_list_products(db, client):
    admin = User(name="Admin", email="admin@example.com", password_hash="hash", role="admin")
    db.add(admin)
    db.commit()
    db.refresh(admin)

    token = create_access_token(admin.email)
    client.headers.update({"Authorization": f"Bearer {token}"})

    create_response = client.post(
        "/products/",
        json={
            "name": "Laptop",
            "description": "Gaming laptop",
            "price": 999.99,
            "stock": 10,
            "image_url": "https://example.com/laptop.jpg",
        },
    )

    assert create_response.status_code == 201
    product_id = create_response.json()["id"]

    list_response = client.get("/products/")
    assert list_response.status_code == 200
    assert any(item["id"] == product_id for item in list_response.json())

    product_response = client.get(f"/products/{product_id}")
    assert product_response.status_code == 200
    assert product_response.json()["name"] == "Laptop"


def test_non_admin_cannot_create_products(db, client):
    customer = User(name="Customer", email="customer@example.com", password_hash="hash", role="customer")
    db.add(customer)
    db.commit()
    db.refresh(customer)

    token = create_access_token(customer.email)
    client.headers.update({"Authorization": f"Bearer {token}"})

    response = client.post(
        "/products/",
        json={
            "name": "Phone",
            "description": "New phone",
            "price": 450.0,
            "stock": 5,
            "image_url": "https://example.com/phone.jpg",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"
