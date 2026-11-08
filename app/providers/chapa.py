import httpx
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
            headers=headers
        )

        pass

    def verify_payment(self, provider_ref):
        pass

    def handle_callback(self, request):
        pass