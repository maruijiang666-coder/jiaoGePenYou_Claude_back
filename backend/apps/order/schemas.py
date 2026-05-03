from ninja import Schema, Field
from datetime import datetime


class CreateOrderRequest(Schema):
    activity_id: int = Field(..., description="活动ID")
    quantity: int = Field(default=1, description="数量")
    total_amount: float = Field(..., description="总金额")
    contact_name: str = Field(default="", description="联系人姓名")
    contact_phone: str = Field(default="", description="联系人电话")
    remark: str = Field(default="", description="备注")


class PayCallbackRequest(Schema):
    order_id: int = Field(..., description="订单ID")


class OrderOut(Schema):
    id: int = Field(..., description="订单ID")
    user_id: int = Field(..., description="用户ID")
    openid: str = Field(default="", description="微信 openid")
    activity_id: int = Field(..., description="活动ID")
    quantity: int = Field(default=1, description="数量")
    total_amount: float = Field(..., description="总金额")
    status: str = Field(default="待付款", description="订单状态（待付款/已付款/已取消/已退款）")
    contact_name: str = Field(default="", description="联系人姓名")
    contact_phone: str = Field(default="", description="联系人电话")
    remark: str = Field(default="", description="备注")
    pay_time: datetime | None = Field(default=None, description="支付时间")
    pay_method: str = Field(default="", description="支付方式")
    refund_time: datetime | None = Field(default=None, description="退款时间")
    transaction_id: str = Field(default="", description="交易流水号")
    created_time: datetime | None = Field(default=None, description="创建时间")
