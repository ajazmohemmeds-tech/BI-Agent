from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import date
from decimal import Decimal

class HealthResponse(BaseModel):
    status: str
    database: str

class SaleOrderResponse(BaseModel):
    id: int
    customer_name: str
    total_amount: Decimal

class ProductResponse(BaseModel):
    id: int
    name: str
    category: str
    list_price: Decimal

class CustomerResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    country: str
    segment: str

class SalesSummaryResponse(BaseModel):
    total_revenue: Decimal
    total_orders: int
    total_customers: int
    best_selling_product: Optional[str]

class RevenueByProductResponse(BaseModel):
    product_name: str
    revenue: Decimal

class RevenueByMonthResponse(BaseModel):
    month: str
    revenue: Decimal

class RevenueByRegionResponse(BaseModel):
    region: str
    revenue: Decimal

class TopCustomerResponse(BaseModel):
    customer_name: str
    total_spend: Decimal

class AIQueryRequest(BaseModel):
    question: str
    history: Optional[List[Dict[str, str]]] = []

class AIQueryResponse(BaseModel):
    explanation: str
    sql_query: str
    results: list
    history: List[Dict[str, str]]
