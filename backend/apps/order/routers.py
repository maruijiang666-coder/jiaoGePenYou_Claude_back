from ninja import Router
from django.shortcuts import get_object_or_404
from core.auth import BearerAuth
from core.pagination import PaginationParams
from .models import Order
from .schemas import CreateOrderRequest, PayCallbackRequest
from .services import mock_payment_params, simulate_pay_callback, simulate_refund

router = Router(auth=BearerAuth())


def order_to_dict(o):
    return {
        "id": o.id, "user_id": o.user_id, "openid": o.openid,
        "activity_id": o.activity_id, "quantity": o.quantity,
        "total_amount": float(o.total_amount), "status": o.status,
        "contact_name": o.contact_name, "contact_phone": o.contact_phone,
        "remark": o.remark, "pay_time": o.pay_time.isoformat() if o.pay_time else None,
        "pay_method": o.pay_method,
        "refund_time": o.refund_time.isoformat() if o.refund_time else None,
        "transaction_id": o.transaction_id,
        "created_time": o.created_time.isoformat() if o.created_time else None,
    }


@router.post("", response=dict)
def create_order(request, body: CreateOrderRequest):
    payload = request.auth
    order = Order.objects.create(
        user_id=payload["user_id"],
        openid=payload["openid"],
        activity_id=body.activity_id,
        quantity=body.quantity,
        total_amount=body.total_amount,
        contact_name=body.contact_name,
        contact_phone=body.contact_phone,
        remark=body.remark,
    )
    payment_params = mock_payment_params(order)
    return {
        "success": True,
        "data": {"order_id": order.id, "payment_params": payment_params},
    }


@router.get("", response=dict)
def list_orders(request, pagination: PaginationParams):
    payload = request.auth
    qs = Order.objects.filter(user_id=payload["user_id"]).order_by("-created_time")
    total = qs.count()
    offset = (pagination.page - 1) * pagination.page_size
    orders = qs[offset:offset + pagination.page_size]
    return {"success": True, "data": {"list": [order_to_dict(o) for o in orders], "total": total}}


@router.get("/{order_id}", response=dict)
def get_order(request, order_id: int):
    payload = request.auth
    order = get_object_or_404(Order, id=order_id, user_id=payload["user_id"])
    return {"success": True, "data": order_to_dict(order)}


@router.post("/pay-callback", response=dict, auth=None)
def pay_callback(request, body: PayCallbackRequest):
    order = get_object_or_404(Order, id=body.order_id)
    simulate_pay_callback(order)
    return {"success": True, "data": {"status": order.status}}


@router.post("/{order_id}/refund", response=dict)
def refund_order(request, order_id: int):
    payload = request.auth
    order = get_object_or_404(Order, id=order_id, user_id=payload["user_id"])
    simulate_refund(order)
    return {"success": True, "data": {"status": order.status}}
