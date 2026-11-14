from decimal import Decimal

import httpx
from fastapi.testclient import TestClient

from app.main import app, payments


client = TestClient(app)

def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == { "status" : "ok"}


def test_initialize_payment(monkeypatch):

    def mock_initiate_payment(self, order):
        return {
            "tx_ref": "test_reference_123",
            "checkout_url": "https://checkout.example.com"
        }

    monkeypatch.setattr(
        "app.main.ChapaProvider.initiate_payment",
        mock_initiate_payment
    )

    response = client.post(
        "/payments",
        json={
            "order_id": 1,
            "amount": "25.00",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User"
        }
    )

    assert response.status_code == 200
    assert response.json()["tx_ref"] == "test_reference_123"


def test_initialize_payment_invalid_amount():

    response = client.post(
        "/payments",
        json={
            "order_id": 1,
            "amount": "-25.00",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User"
        }
    )

    assert response.status_code == 422



def test_get_payment(monkeypatch):
    tx_ref = "test_reference_123"

    monkeypatch.setitem(payments, tx_ref, {
        "order_id": 1,
        "amount": Decimal("25.00"),
        "currency": "ETB"
    })

    def mock_verify_payment(self, provider_ref):
        return {
            "tx_ref": tx_ref,
            "amount": 25,
            "currency": "ETB",
            "status": "success"
        }

    monkeypatch.setattr(
        "app.main.ChapaProvider.verify_payment",
        mock_verify_payment
    )

    response = client.get(f"/payments/{tx_ref}")

    assert response.status_code == 200
    assert response.json()["status"] == "success"


def test_get_payment_not_found():
    response = client.get("/payments/nonexistent_reference")

    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found!"


def test_payment_callback(monkeypatch):
    tx_ref = "callback_test_123"

    monkeypatch.setitem(payments, tx_ref, {
        "order_id": 2,
        "amount": Decimal("25.00"),
        "currency": "ETB"
    })

    async def mock_handle_callback(self, request):
        return {
            "tx_ref": tx_ref,
            "amount": 25,
            "currency": "ETB",
            "status": "success"
        }

    monkeypatch.setattr(
        "app.main.ChapaProvider.handle_callback",
        mock_handle_callback
    )

    response = client.post(
        "/payments/callback",
        json={"trx_ref": tx_ref}
    )

    assert response.status_code == 200
    assert response.json()["tx_ref"] == tx_ref
    assert response.json()["status"] == "success"


def test_payment_callback_not_found(monkeypatch):
    async def mock_handle_callback(self, request):
        return {
            "tx_ref": "unknown_reference",
            "amount": 25,
            "currency": "ETB",
            "status": "success"
        }

    monkeypatch.setattr(
        "app.main.ChapaProvider.handle_callback",
        mock_handle_callback
    )

    response = client.post(
        "/payments/callback",
        json={"trx_ref": "unknown_reference"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Payment record not found."


def test_payment_callback_missing_reference():
    response = client.post(
        "/payments/callback",
        json={}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Transaction reference is required."


def test_initialize_payment_timeout(monkeypatch):
    def mock_initiate_payment(self, order):
        raise httpx.TimeoutException("Request timed out")

    monkeypatch.setattr(
        "app.main.ChapaProvider.initiate_payment",
        mock_initiate_payment
    )

    response = client.post(
        "/payments",
        json={
            "order_id": 1,
            "amount": "25.00",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User"
        }
    )

    assert response.status_code == 504
    assert response.json()["detail"] == "Payment gateway request timed out."


def test_initialize_payment_http_error(monkeypatch):
    def mock_initiate_payment(self, order):
        request = httpx.Request("POST", "https://api.chapa.co/v1/transaction/initialize")
        response = httpx.Response(500, request=request)
        raise httpx.HTTPStatusError(
            "Server error",
            request=request,
            response=response
        )

    monkeypatch.setattr(
        "app.main.ChapaProvider.initiate_payment",
        mock_initiate_payment
    )

    response = client.post(
        "/payments",
        json={
            "order_id": 1,
            "amount": "25.00",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User"
        }
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Payment gateway returned an unsuccessful response."



def test_initialize_payment_connection_error(monkeypatch):
    def mock_initiate_payment(self, order):
        request = httpx.Request(
            "POST",
            "https://api.chapa.co/v1/transaction/initialize"
        )
        raise httpx.ConnectError(
            "Connection failed",
            request=request
        )

    monkeypatch.setattr(
        "app.main.ChapaProvider.initiate_payment",
        mock_initiate_payment
    )

    response = client.post(
        "/payments",
        json={
            "order_id": 1,
            "amount": "25.00",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User"
        }
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Unable to connect to payment gateway"


def test_get_payment_amount_mismatch(monkeypatch):
    tx_ref = "amount_mismatch_123"

    monkeypatch.setitem(payments, tx_ref, {
        "order_id": 3,
        "amount": Decimal("25.00"),
        "currency": "ETB"
    })

    def mock_verify_payment(self, provider_ref):
        return {
            "tx_ref": tx_ref,
            "amount": 20,
            "currency": "ETB",
            "status": "success"
        }

    monkeypatch.setattr(
        "app.main.ChapaProvider.verify_payment",
        mock_verify_payment
    )

    response = client.get(f"/payments/{tx_ref}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Payment amount does not match the original order."


def test_get_payment_currency_mismatch(monkeypatch):
    tx_ref = "currency_mismatch_123"

    monkeypatch.setitem(payments, tx_ref, {
        "order_id": 4,
        "amount": Decimal("25.00"),
        "currency": "ETB"
    })

    def mock_verify_payment(self, provider_ref):
        return {
            "tx_ref": tx_ref,
            "amount": 25,
            "currency": "USD",
            "status": "success"
        }

    monkeypatch.setattr(
        "app.main.ChapaProvider.verify_payment",
        mock_verify_payment
    )

    response = client.get(f"/payments/{tx_ref}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Payment currency does not match the original order."
