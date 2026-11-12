import httpx
from app.providers.chapa import ChapaProvider
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from decimal import Decimal


app = FastAPI()

payments = {}

class Order(BaseModel):
    order_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0)
    email: str
    first_name: str
    last_name: str

@app.get("/health")
def health_check():
    return { "status" : "ok"}

@app.post("/payments")
def initialize_payment(order: Order):
    provider = ChapaProvider()

    try:
        result = provider.initiate_payment(order)

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Payment gateway request timed out."
        )

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail="Payment gateway returned an unsuccessful response."
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Unable to connect to payment gateway"
        )

    payments[result["tx_ref"]] = {
        "order_id": order.order_id,
        "amount": order.amount,
        "currency": "ETB"
    }

    return result

@app.post("/payments/callback")
async def callback(request: Request):
    provider = ChapaProvider()

    try:
        verified_data = await provider.handle_callback(request)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
    
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Payment gateway request timed out."
        )

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail="Payment gateway returned an unsuccessful response."
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Unable to connect to payment gateway"
        )

    payment = payments.get(verified_data["tx_ref"])

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment record not found."
        )

    if Decimal(str(verified_data["amount"])) != payment["amount"]:
        raise HTTPException(
            status_code=400,
            detail="Payment amount does not match the original order."
        )
    
    if verified_data["currency"] != payment["currency"]:
        raise HTTPException(
            status_code=400,
            detail="Payment currency does not match the original order."
        )

    return verified_data

@app.get("/payments/{tx_ref}")
def get_payment(tx_ref: str):
    payment = payments.get(tx_ref)

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found!"
        )

    provider = ChapaProvider()

    try:
        verified_data = provider.verify_payment(tx_ref)
    
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Payment gateway request timed out."
        )

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail="Payment gateway returned an unsuccessful response."
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Unable to connect to payment gateway"
        )

    if verified_data["tx_ref"] != tx_ref:
        raise HTTPException(
            status_code=400,
            detail="Transaction reference does not match."
        )

    if Decimal(str(verified_data["amount"])) != payment["amount"]:
        raise HTTPException(
            status_code=400,
            detail="Payment amount does not match the original order."
        )
    
    if verified_data["currency"] != payment["currency"]:
        raise HTTPException(
            status_code=400,
            detail="Payment currency does not match the original order."
        )

    return verified_data




