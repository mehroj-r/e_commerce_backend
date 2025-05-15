import time
import base64
import requests
from jsonrpcclient import request
from django.conf import settings

class PaymeClient:
    def __init__(self):
        self.base_url = settings.PAYME_CHECKOUT_URL
        self.auth_header = self._build_auth_header(settings.PAYME_MERCHANT_ID, settings.PAYME_SECRET_KEY)

    def _build_auth_header(self, username, password):
        """
        Encodes username and password in base64 for HTTP Basic Auth.

        Args:
            username (str): Merchant ID
            password (str): Secret Key
        Returns:
            str: Value for the 'Authorization' header.
        """
        credentials = f"{username}:{password}"
        encoded = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        return f"Basic {encoded}"

    def call(self, method, params=None):
        """
        Helper to make RPC calls.

        Args:
            method (str): The method to call.
            params (dict): The parameters to pass to the method.
        Returns:
            response (dict): The response from the RPC call.
        """

        # Generate RPC payload
        rpc_data = request(method, params or {})

        # Headers to be included
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Authorization": self.auth_header,
        }

        try:

            # Send the request to the API endpoint
            response = requests.post(
                self.base_url,
                headers=headers,
                json=rpc_data
            )

            # Check HTTP status code first
            response.raise_for_status()

            # Parse JSON response
            response_data = response.json()

            # Check for error in the response
            if "error" in response_data:
                error_msg = "Unknown error"
                if isinstance(response_data["error"], dict):
                    # Try to extract the error message based on Payme API format
                    if "message" in response_data["error"]:
                        if isinstance(response_data["error"]["message"], dict) and "en" in response_data["error"][
                            "message"]:
                            error_msg = response_data["error"]["message"]["en"]
                        else:
                            error_msg = str(response_data["error"]["message"])
                    elif "data" in response_data["error"]:
                        error_msg = str(response_data["error"]["data"])
                    else:
                        error_msg = str(response_data["error"])
                else:
                    error_msg = str(response_data["error"])

                raise Exception(f"API Error: {error_msg}")

            # Ensure result exists in the response
            if "result" not in response_data:
                raise Exception("Invalid API response: missing 'result'")

            # Return the response
            return response_data["result"]

        except requests.exceptions.RequestException as e:
            raise Exception(f"RPC request failed: {str(e)}")

    def check_perform_transaction(self, payment):
        """
        Checks if transaction can be performed.

        Args:
            payment: Payment model instance
        Returns:
            response (dict): The response from the RPC call.
        """
        # Create account dict from order
        account = {
            "order_id": str(payment.order.id)
        }

        # Define method parameters
        params = {
            "amount": payment.get_amount_in_tiyins(),
            "account": account
        }

        # Call CheckPerformTransaction method
        return self.call("CheckPerformTransaction", params)

    def create_transaction(self, payment):
        """
        Creates a transaction in Payme system.

        Args:
            payment: Payment model instance
        Returns:
            response (dict): The response from the RPC call.
        """
        # Get current time in milliseconds
        current_time = int(time.time() * 1000)

        # Create account dict
        account = {
            "order_id":str(payment.order.id)
        }

        # Define method parameters
        params = {
            "id":payment.payment_id,
            "time":current_time,
            "amount":payment.get_amount_in_tiyins(),
            "account":account
        }

        # Save transaction time
        payment.provider_transaction_time = current_time
        payment.save()

        # Call CreateTransaction method
        return self.call("CreateTransaction", params)

    def perform_transaction(self, payment):
        """
        Performs a transaction.

        Args:
            payment: Payment model instance
        Returns:
            response (dict): The response from the RPC call.
        """

        # Define method parameters
        params = {
            "id":payment.provider_transaction_id
        }

        # Call PerformTransaction method
        return self.call("PerformTransaction", params)

    def cancel_transaction(self, payment, reason):
        """
        Cancels a transaction.

        Args:
            payment: Payment model instance
            reason (int): The reason code for cancellation
        Returns:
            response (dict): The response from the RPC call.
        """

        # Define method parameters
        params = {
            "id": payment.provider_transaction_id,
            "reason": reason
        }

        # Call CancelTransaction method
        return self.call("CancelTransaction", params)

    def check_transaction(self, payment):
        """
        Checks the status of a transaction.

        Args:
            payment: Payment model instance
        Returns:
            response (dict): The response from the RPC call.
        """

        # Define method parameters
        params = {
            "id": payment.provider_transaction_id
        }

        # Call CheckTransaction method
        return self.call("CheckTransaction", params)