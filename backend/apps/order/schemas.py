from ninja import Schema
from datetime import datetime


class CreateOrderRequest(Schema):
    activity_id: int
    quantity: int = 1
    total_amount: float
    contact_name: str = ""
    contact_phone: str = ""
    remark: str = ""


class PayCallbackRequest(Schema):
    order_id: int


class OrderOut(Schema):
    id: int
    user_id: int
    openid: str = ""
    activity_id: int
    quantity: int = 1
    total_amount: float
    status: str = "待付款"
    contact_name: str = ""
    contact_phone: str = ""
    remark: str = ""
    pay_time: datetime | None = None
    pay_method: str = ""
    refund_time: datetime | None = None
    transaction_id: str = ""
    created_time: datetime | None = None
