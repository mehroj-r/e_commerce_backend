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

        # Geneerate RPC payload
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
            ).json()

            # Raise exception if 'error' occurs
            if response.status_code != 200 or "error" in response:
                raise Exception(f"Error: {response["error"]["message"]["en"]}")

            # Return the reponse
            return response["result"]

        except requests.exceptions.RequestException as e:
            raise Exception(f"RPC request failed: {str(e)}")

    def checkPerformTransaction(self, amount, account):
        """
        Checks if transaction can be performed.

        Args:
            amount (int): The amount to be checked.
            account (dict): The account to check.

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
            id (str): The id of the transaction.
            time (int): The creation time of the transaction.
            amount (int): The amount of the transaction.
            account (dict): The account to create the transaction.

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
            id (str): The id of the transaction.
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
            id (str): The id of the transaction.
            reason (int): The reason for the transaction.
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
        Checks the transaction.

        Args:
            id (str): The id of the transaction.
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


