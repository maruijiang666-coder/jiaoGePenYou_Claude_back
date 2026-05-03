import uuid
from datetime import datetime
from .models import Order


def mock_payment_params(order: Order) -> dict:
    return {
        "timeStamp": str(int(datetime.now().timestamp())),
        "nonceStr": uuid.uuid4().hex[:32],
        "package": "prepay_id=mock_" + uuid.uuid4().hex[:16],
        "signType": "MD5",
        "paySign": "MOCK_PAY_SIGN",
    }


def simulate_pay_callback(order: Order) -> None:
    from django.utils import timezone
    order.status = "已付款"
    order.pay_time = timezone.now()
    order.pay_method = "微信支付(MOCK)"
    order.transaction_id = "MOCK_TXN_" + uuid.uuid4().hex[:16]
    order.save()


def simulate_refund(order: Order) -> None:
    from django.utils import timezone
    if order.status != "已付款":
        raise Exception("只有已付款的订单可以退款")
    order.status = "已退款"
    order.refund_time = timezone.now()
    order.save()
