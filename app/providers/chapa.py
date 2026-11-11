import httpx
from fastapi import Request
from app.providers.base import PaymentProvider
from app.config import chapa_secret_key, chapa_base_url, callback_url
from uuid import uuid4



class ChapaProvider(PaymentProvider):

    def initiate_payment(self, order):
        reference = uuid4().hex

        url = f"{chapa_base_url}/transaction/initialize"

        headers = {
            "Authorization": f"Bearer {chapa_secret_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "amount": str(order.amount),
            "currency": "ETB",
            "email": order.email,
            "first_name": order.first_name,
            "last_name": order.last_name,
            "tx_ref": reference,
            "callback_url": callback_url
        }

        response = httpx.post(
            url,
            json=payload,
            headers=headers,
            timeout=10.0
        )

        response.raise_for_status()
        response_data = response.json()
        
        if response_data.get("status") != "success":
            raise Exception("Payment initialization failed")

        checkout_url = response_data["data"]["checkout_url"]

        return {
            "tx_ref": reference,
            "checkout_url": checkout_url
        }


    def verify_payment(self, provider_ref):
        url = f"{chapa_base_url}/transaction/verify/{provider_ref}"

        headers = {
            "Authorization": f"Bearer {chapa_secret_key}",
            "Content-Type": "application/json"
        }

        response = httpx.get(
            url,
            headers=headers,
            timeout=10.0
        )

        response.raise_for_status()
        response_data = response.json()

        if response_data.get("status") != "success":
            raise Exception("Verification process failed")

        return response_data["data"]

    async def handle_callback(self, request: Request):
        callback_data = await request.json()
        provider_ref = callback_data.get("trx_ref")

        if not provider_ref:
            raise ValueError("Transaction reference is required.")

        verified_data = self.verify_payment(provider_ref)

        return verified_data