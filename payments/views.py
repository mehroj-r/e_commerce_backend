import base64
import random

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.conf import settings

import logging

from app.models import Order, Payment
from .payme_client import PaymeClient

logger = logging.getLogger(__name__)

@login_required
def checkout(request, order_id):
    """
    Display checkout page for an order
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Check if payment already exists
    payment = Payment.objects.filter(order=order, status=Payment.PaymentStatus.PENDING).first()

    if not payment:
        payment = Payment.create_for_order(order)

    context = {
        'order':order,
        'payment':payment,
        'payme_merchant_id':settings.PAYME_MERCHANT_ID,
    }

    return render(request, 'payments/checkout.html', context)


@login_required
def init_payme_payment(request, order_id):
    """
    Initialize a payment with Payme
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Check if payment already exists
    payment = Payment.objects.filter(order=order, status=Payment.PaymentStatus.PENDING).first()

    if not payment:
        payment = Payment.create_for_order(order)

    # Get redirect URL for payment
    try:
        client = PaymeClient()

        # Check if transaction can be performed:
        # check_result = client.check_perform_transaction(payment)
        check_result = {
            "allow" : True
        }

        if check_result.get('allow') is not True:
            return JsonResponse({
                'success': False,
                'error': 'Payment not allowed by Payme'
            })


        # Create transaction
        # transaction_result = client.create_transaction(payment)
        transaction_result = {
            "create_time": payment.created_at.isoformat(),
            "transaction": f"{random.randint(1000, 9999)}",
            "state": 1
        }

        # Save transaction ID
        payment.provider_transaction_id = transaction_result.get('transaction')
        payment.provider_payment_data = transaction_result
        payment.save()

        # Generate ULR form to redirect to Payme Payment page
        merchant_id = f"m={settings.PAYME_MERCHANT_ID};"
        order_id = f"ac.order_id={order.id};"
        amount = f"a={payment.get_amount_in_tiyins()};"
        lang = f"l={"en"};"
        cancel_address = f"c={settings.BASE_URL}/cancel-payment/{payment.id}"
        url_form = merchant_id+order_id+amount+lang+cancel_address

        # Encode 'url_form' in base64
        url_encoded = base64.b64encode(url_form.encode('utf-8')).decode('utf-8')
        print(url_encoded)

        # Return success with transaction data
        return JsonResponse({
            'success': True,
            'transaction_id': payment.provider_transaction_id,
            'redirect_url': f"{settings.PAYME_CHECKOUT_URL}/{url_encoded}"
        })

    except Exception as e:
        logger.error(f"Payme payment initialization error: {str(e)}")
        return JsonResponse({
            'success':False,
            'error':str(e)
        }, status=400)


@login_required
def payment_status(request, payment_id):
    """
    Check payment status
    """
    payment = get_object_or_404(Payment, payment_id=payment_id)

    # Verify user owns the order
    if payment.order.user != request.user:
        return HttpResponseBadRequest("Unauthorized")

    try:
        client = PaymeClient()
        # status = client.check_transaction(payment)
        status = {
            "create_time" : payment.created_at.isoformat(),
            "perform_time" : payment.created_at.isoformat(),
            "cancel_time" : 0,
            "transaction" : payment.provider_transaction_id,
            "state" : 2,
            "reason" : None
        }


        # Update payment status based on Payme response
        if status.get('state') == 2:
            payment.status = Payment.PaymentStatus.PAID
            payment.order.status = Order.OrderStatus.PAID
            payment.order.save()
        elif status.get('state') == -1:
            payment.status = Payment.PaymentStatus.CANCELED
        elif status.get('state') == -2:
            payment.status = Payment.PaymentStatus.REFUNDED
        elif status.get('state') == 1:
            pass

        payment.save()

        return JsonResponse({
            'success':True,
            'status':payment.status,
            'payment_data':status
        })

    except Exception as e:
        logger.error(f"Payment status check error: {str(e)}")
        return JsonResponse({
            'success':False,
            'error':str(e)
        }, status=400)