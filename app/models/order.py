from decimal import Decimal
from pydantic import BaseModel, Field


class Order(BaseModel):
    order_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0)
    email: str
    first_name: str
    last_name: str