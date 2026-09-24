import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class InventoryServiceError(Exception):
    """Base exception for Inventory integration errors."""


class InventoryConnectionError(InventoryServiceError):
    """Raised when the Inventory System cannot be reached."""


class InventoryTransactionError(InventoryServiceError):
    """Raised when the Inventory System rejects a stock transaction."""


@dataclass
class InventoryResult:
    success: bool
    data: Any = None
    message: str | None = None


class InventoryService:
    """
    Service layer responsible for communication between the Clinic
    System and the external Inventory System.

    The Clinic backend should use this service instead of calling
    Inventory endpoints directly from views.
    """

    def __init__(self, base_url: str | None = None, timeout: int = 5):
        self.base_url = (
            base_url
            or os.getenv(
                "INVENTORY_API_BASE_URL",
                "http://127.0.0.1:8000",
            )
        ).rstrip("/")

        self.timeout = timeout

    def _request(
        self,
        method: str,
        endpoint: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Send an HTTP request to the Inventory System and return
        the decoded JSON response.
        """

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        headers = {
            "Accept": "application/json",
        }

        data = None

        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(
            url=url,
            data=data,
            headers=headers,
            method=method.upper(),
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
            ) as response:
                response_body = response.read().decode("utf-8")

        except urllib.error.HTTPError as exc:
            try:
                error_body = exc.read().decode("utf-8")
                error_data = json.loads(error_body)
            except (json.JSONDecodeError, UnicodeDecodeError):
                error_data = {}

            message = (
                error_data.get("message")
                or error_data.get("detail")
                or f"Inventory System returned HTTP {exc.code}."
            )

            raise InventoryServiceError(message) from exc

        except (
            urllib.error.URLError,
            TimeoutError,
            ConnectionError,
        ) as exc:
            raise InventoryConnectionError(
                "Unable to connect to the Inventory System."
            ) from exc

        try:
            result = json.loads(response_body)
        except json.JSONDecodeError as exc:
            raise InventoryServiceError(
                "Inventory System returned an invalid JSON response."
            ) from exc

        if not isinstance(result, dict):
            raise InventoryServiceError(
                "Inventory System returned an invalid response format."
            )

        return result

    def get_stock(self) -> list[dict[str, Any]]:
        """
        Retrieve medicine stock from the Inventory System.

        Expected external Inventory response:

        {
            "success": true,
            "source": "Inventory Management System",
            "data": [
                {
                    "product_id": 1,
                    "product_name": "Paracetamol",
                    "stock": 50
                }
            ]
        }
        """

        result = self._request(
            method="GET",
            endpoint="/backend/integration.php?action=stock",
        )

        if result.get("success") is not True:
            raise InventoryServiceError(
                result.get(
                    "message",
                    "Unable to retrieve medicine stock from Inventory System.",
                )
            )

        stock_data = result.get("data")

        if not isinstance(stock_data, list):
            raise InventoryServiceError(
                "Inventory System returned invalid stock data."
            )

        return stock_data

    def dispense_stock(
        self,
        medicine_id: int,
        quantity: int,
        remarks: str | None = None,
    ) -> InventoryResult:
        """
        Request the Inventory System to deduct medicine stock.

        External Inventory request:

        {
            "product_id": medicine_id,
            "movement_type": "OUT",
            "quantity": quantity,
            "remarks": "Clinic medicine dispensing"
        }
        """

        if medicine_id < 1:
            raise ValueError("medicine_id must be greater than 0.")

        if quantity < 1:
            raise ValueError("quantity must be greater than 0.")

        payload = {
            "product_id": medicine_id,
            "movement_type": "OUT",
            "quantity": quantity,
            "remarks": remarks or "Clinic medicine dispensing",
        }

        result = self._request(
            method="POST",
            endpoint="/backend/stock.php",
            payload=payload,
        )

        if result.get("success") is not True:
            raise InventoryTransactionError(
                result.get(
                    "message",
                    "Inventory System rejected the stock transaction.",
                )
            )

        return InventoryResult(
            success=True,
            data=result,
            message=result.get("message"),
        )


def get_inventory_stock() -> list[dict[str, Any]]:
    """
    Convenience function for retrieving Inventory stock.
    """
    return InventoryService().get_stock()
    

def dispense_inventory_stock(
    medicine_id: int,
    quantity: int,
    remarks: str | None = None,
) -> InventoryResult:
    """
    Convenience function for dispensing medicine stock.
    """
    return InventoryService().dispense_stock(
        medicine_id=medicine_id,
        quantity=quantity,
        remarks=remarks,
    )