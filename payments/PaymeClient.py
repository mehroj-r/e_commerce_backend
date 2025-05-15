import base64
import requests
from jsonrpcclient import request

class PaymeClient:

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.auth_header = self._build_auth_header(username, password)

    def _build_auth_header(self, username, password):
        """
        Encodes username and password in base64 for HTTP Basic Auth.

        Args:
            username (str): Username
            password (str): Password

        Returns:
            str: Value for the 'Authorization' header.
        """
        credentials = f"{username}:{password}"
        encoded = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        return f"Basic {encoded}"

    def call(self, method, params=None):
        """
        Helper to make rpc calls.

        Args:
            method (str): The method to call.
            params (dict): The parameters to pass to the method.

        Returns:
            response (dict): The response from the rpc call.
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

    def checkPerformTransaction(self, amount, account):
        """
        Checks if transaction can be performed.

        Args:
            amount (int): The amount to be checked (in tiyins/kopecks).
            account (dict): The account to check (format depends on merchant requirements).

        Returns:
            response (dict): The response from the rpc call.
        """

        # Define properties
        method = "CheckPerformTransaction"
        params = {
            "amount": amount,
            "account": account
        }

        # Make RPC request
        response = self.call(
            method,
            params
        )

        return response

    def createTransaction(self, id, time, amount, account):
        """
        Creates a transaction.

        Args:
            id (str): The id of the transaction (must be unique).
            time (int): The creation time of the transaction (milliseconds since epoch).
            amount (int): The amount of the transaction (in tiyins/kopecks).
            account (dict): The account to create the transaction for.

        Returns:
            response (dict): The response from the rpc call.
        """

        # Define properties
        method = "CreateTransaction"
        params = {
            "id": id,
            "time": time,
            "amount": amount,
            "account": account
        }

        # Make RPC request
        response = self.call(
            method,
            params
        )

        return response

    def performTransaction(self, id):
        """
        Performs a transaction.

        Args:
            id (str): The id of the transaction to perform.
        Returns:
            response (dict): The response from the rpc call.
        """

        # Define properties
        method = "PerformTransaction"
        params = {
            "id": id
        }

        # Make RPC request
        response = self.call(
            method,
            params
        )

        return response

    def cancelTransaction(self, id, reason):
        """
        Cancels a transaction.

        Args:
            id (str): The id of the transaction to cancel.
            reason (int): The reason code for cancellation.
        Returns:
            response (dict): The response from the rpc call.
        """

        # Define properties
        method = "CancelTransaction"
        params = {
            "id": id,
            "reason": reason
        }

        # Make RPC request
        response = self.call(
            method,
            params
        )

        return response

    def checkTransaction(self, id):
        """
        Checks the status of a transaction.

        Args:
            id (str): The id of the transaction to check.
        Returns:
            response (dict): The response from the rpc call.
        """

        # Define properties
        method = "CheckTransaction"
        params = {
            "id": id
        }

        # Make RPC request
        response = self.call(
            method,
            params
        )

        return response