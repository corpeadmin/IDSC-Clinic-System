from http.server import BaseHTTPRequestHandler, HTTPServer
import json


HOST = "127.0.0.1"
PORT = 8200


STUDENTS = {
    24: {
        "id": 24,
        "studentNumber": "2026-001",
        "firstName": "Juan",
        "lastName": "Dela Cruz",
        "email": "juan.delacruz@example.com",
        "program": "Bachelor of Science in Information Technology",
        "yearLevel": 3,
        "status": "Active",
    }
}


class RegistrarHandler(BaseHTTPRequestHandler):

    def send_json(self, status_code, data):
        response = json.dumps(data).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()

        self.wfile.write(response)

    def do_GET(self):
        path = self.path.rstrip("/")

        # GET /api/v1/students/{id}
        if path.startswith("/api/v1/students/"):
            student_id_text = path.split("/")[-1]

            try:
                student_id = int(student_id_text)
            except ValueError:
                self.send_json(
                    400,
                    {
                        "code": "BAD_REQUEST",
                        "message": "Student ID must be an integer.",
                    },
                )
                return

            student = STUDENTS.get(student_id)

            if student is None:
                self.send_json(
                    404,
                    {
                        "code": "RESOURCE_NOT_FOUND",
                        "message": "The requested student was not found.",
                    },
                )
                return

            self.send_json(200, student,)
            return

        # GET /api/v1/health
        if path == "/api/v1/health":
            self.send_json(
                200,
                {
                    "status": "healthy",
                    "service": "mock-registrar",
                    "version": "1.0.0",
                },
            )
            return

        self.send_json(
            404,
            {
                "code": "RESOURCE_NOT_FOUND",
                "message": "The requested resource was not found.",
            },
        )

    def log_message(self, format, *args):
        print(f"[Registrar] {self.address_string()} - {format % args}")


def run():
    server = HTTPServer((HOST, PORT), RegistrarHandler)

    print("=" * 50)
    print("Mock Registrar System")
    print("=" * 50)
    print(f"Running at: http://{HOST}:{PORT}")
    print("Student endpoint:")
    print(f"  GET http://{HOST}:{PORT}/api/v1/students/24")
    print()
    print("Press CTRL+C to stop.")
    print("=" * 50)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nMock Registrar stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    run()