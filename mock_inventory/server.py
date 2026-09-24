import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse


HOST = "127.0.0.1"
PORT = 8100


# Temporary mock Inventory data.
# These represent products owned by the external Inventory System.
PRODUCTS = {
    1: {
        "id": 1,
        "product_name": "Paracetamol",
        "category": "Medicine",
        "price": 5.00,
        "stock": 50,
        "available": True,
    },
    2: {
        "id": 2,
        "product_name": "Ibuprofen",
        "category": "Medicine",
        "price": 8.00,
        "stock": 0,
        "available": False,
    },
    3: {
        "id": 3,
        "product_name": "Amoxicillin",
        "category": "Medicine",
        "price": 12.00,
        "stock": 25,
        "available": True,
    },
}


def update_availability(product):
    product["available"] = product["stock"] > 0


class MockInventoryHandler(BaseHTTPRequestHandler):
    """
    Temporary mock of the external Inventory System.

    Implemented endpoints:

    GET:
        /backend/integration.php?action=stock

    POST:
        /backend/stock.php
    """

    def send_json(self, status_code, data):
        response = json.dumps(data).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        query = parse_qs(parsed_url.query)

        # Inventory stock endpoint
        if (
            parsed_url.path == "/backend/integration.php"
            and query.get("action", [None])[0] == "stock"
        ):
            stock_data = [
                {
                    "product_id": product["id"],
                    "product_name": product["product_name"],
                    "stock": product["stock"],
                }
                for product in PRODUCTS.values()
            ]

            self.send_json(
                200,
                {
                    "success": True,
                    "source": "Inventory Management System",
                    "data": stock_data,
                },
            )
            return

        self.send_json(
            404,
            {
                "success": False,
                "message": "Endpoint not found.",
            },
        )

    def do_POST(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path != "/backend/stock.php":
            self.send_json(
                404,
                {
                    "success": False,
                    "message": "Endpoint not found.",
                },
            )
            return

        content_length = self.headers.get("Content-Length")

        if not content_length:
            self.send_json(
                400,
                {
                    "success": False,
                    "message": "Request body is required.",
                },
            )
            return

        try:
            raw_body = self.rfile.read(int(content_length))
            payload = json.loads(raw_body.decode("utf-8"))
        except (ValueError, json.JSONDecodeError):
            self.send_json(
                400,
                {
                    "success": False,
                    "message": "Invalid JSON request body.",
                },
            )
            return

        product_id = payload.get("product_id")
        movement_type = payload.get("movement_type")
        quantity = payload.get("quantity")
        remarks = payload.get("remarks")

        if product_id is None:
            self.send_json(
                400,
                {
                    "success": False,
                    "message": "product_id is required.",
                },
            )
            return

        if movement_type not in ("IN", "OUT"):
            self.send_json(
                400,
                {
                    "success": False,
                    "message": "movement_type must be IN or OUT.",
                },
            )
            return

        if not isinstance(quantity, int) or quantity < 1:
            self.send_json(
                400,
                {
                    "success": False,
                    "message": "quantity must be a positive integer.",
                },
            )
            return

        try:
            product_id = int(product_id)
        except (TypeError, ValueError):
            self.send_json(
                400,
                {
                    "success": False,
                    "message": "product_id must be an integer.",
                },
            )
            return

        product = PRODUCTS.get(product_id)

        if product is None:
            self.send_json(
                404,
                {
                    "success": False,
                    "message": "Product not found.",
                },
            )
            return

        # Stock IN
        if movement_type == "IN":
            product["stock"] += quantity
            update_availability(product)

            self.send_json(
                200,
                {
                    "success": True,
                    "message": "Stock updated successfully.",
                    "new_stock": product["stock"],
                },
            )
            return

        # Stock OUT
        if quantity > product["stock"]:
            self.send_json(
                400,
                {
                    "success": False,
                    "message": "Not enough stock available.",
                },
            )
            return

        product["stock"] -= quantity
        update_availability(product)

        self.send_json(
            200,
            {
                "success": True,
                "message": "Stock updated successfully.",
                "new_stock": product["stock"],
            },
        )

    def log_message(self, format, *args):
        print(f"[Mock Inventory] {self.address_string()} - {format % args}")


def run_server():
    server = HTTPServer((HOST, PORT), MockInventoryHandler)

    print("=" * 60)
    print("Mock Inventory API")
    print("=" * 60)
    print(f"Server running at: http://{HOST}:{PORT}")
    print()
    print("Available endpoints:")
    print(
        f"GET  http://{HOST}:{PORT}/backend/integration.php?action=stock"
    )
    print(
        f"POST http://{HOST}:{PORT}/backend/stock.php"
    )
    print()
    print("Initial stock:")
    for product in PRODUCTS.values():
        print(
            f"  [{product['id']}] "
            f"{product['product_name']}: "
            f"{product['stock']}"
        )
    print()
    print("Press CTRL+C to stop the server.")
    print("=" * 60)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Mock Inventory API...")
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()