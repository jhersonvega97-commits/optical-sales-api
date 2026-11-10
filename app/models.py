from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

class SalespersonCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    monthly_target: Decimal = Field(ge=0, max_digits=12, decimal_places=2)

    @field_validator('name')
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError('name must not be blank')
        return value

class OrderCreate(BaseModel):
    salesperson_id: int = Field(gt=0)
    customer_name: str = Field(min_length=1, max_length=100)
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

    @field_validator('customer_name')
    @classmethod
    def customer_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError('customer name must not be blank')
        return value

class SalespersonRead(BaseModel):
    id: int
    name: str
    monthly_target: Decimal

class OrderRead(BaseModel):
    id: int
    salesperson_id: int
    customer_name: str
    amount: Decimal

class SalesSummary(BaseModel):
    salesperson_id: int
    salesperson_name: str
    monthly_target: Decimal
    total_sales: Decimal
    attainment_percent: Decimal | None
    order_count: int
