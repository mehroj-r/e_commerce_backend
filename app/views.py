from django.http import HttpResponse

def cancel_payment(request):
    """
    Payment cancel page when payment is canceled.
    """

    payment_id = request.GET.get('payment_id')

    return HttpResponse(f"You payment was cancelled. Payment id: {payment_id}")