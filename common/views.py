from django.shortcuts import redirect
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponseRedirect
from sslcommerz_lib import SSLCOMMERZ
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from orders.models import Order, OrderItem
from django.conf import settings as main_settings

def redirect_from_base(request):
    return redirect('/swagger/')


import uuid

@api_view(['POST'])
def initiate_payment(request):
    user = request.user
    amount = request.data.get("amount")
    order_id = request.data.get("orderId")
    num_items = request.data.get("numItems")

    settings = {
        'store_id': 'servi68c02a8fe33a3',
        'store_pass': 'servi68c02a8fe33a3@ssl',
        'issandbox': True
    }
    sslcz = SSLCOMMERZ(settings)

    post_body = {
        'total_amount': amount,
        'currency': "BDT",
        'tran_id': f"txn_{order_id}_{uuid.uuid4().hex[:6]}",
        'success_url': f"{main_settings.BACKEND_URL}/api/payment/success/",
        'fail_url': f"{main_settings.BACKEND_URL}/api/payment/fail/",
        'cancel_url': f"{main_settings.BACKEND_URL}/api/payment/cancel/",
        'emi_option': 0,
        'cus_name': f"{user.first_name} {user.last_name}".strip() or "Customer",
        'cus_email': user.email or "test@example.com",
        'cus_phone': getattr(user.profile, "phone_number", "01711111111"),
        'cus_add1': getattr(user.profile, "address", "Dhaka"),
        'cus_city': "Dhaka",
        'cus_country': "Bangladesh",
        'shipping_method': "NO",
        'multi_card_name': "",
        'num_of_item': num_items or 1,
        'product_name': "Household Services",
        'product_category': "General",
        'product_profile': "general",
    }

    response = sslcz.createSession(post_body)

    if response.get("status") == 'SUCCESS':
        return Response({"payment_url": response['GatewayPageURL']})

    return Response({"error": response.get("failedreason", "Payment initiation failed")}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
def payment_success(request):
    order_id = request.data.get("tran_id").split('_')[1]
    order = Order.objects.get(id=order_id)
    order.status = "ACCEPTED"
    order.save()
    return HttpResponseRedirect(f"{main_settings.FRONTEND_URL}/dashboard/payment/success/")


@api_view(['POST'])
def payment_cancel(request):
    return HttpResponseRedirect(f"{main_settings.FRONTEND_URL}/dashboard/payment/cancel/")


@api_view(['POST'])
def payment_fail(request):
    return HttpResponseRedirect(f"{main_settings.FRONTEND_URL}/dashboard/payment/fail/")
    