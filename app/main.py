import httpx
from app.providers.chapa import ChapaProvider
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from decimal import Decimal


app = FastAPI()

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

    return verified_data

    



