from fastapi import FastAPI
from pydantic import BaseModel, Field
from decimal import Decimal


app = FastAPI()

class Order(BaseModel):
    order_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0)

@app.get("/health")
def health_check():
    return { "status" : "ok"}

@app.post("/orders")
def create_order(order: Order):
    return order.model_dump()


