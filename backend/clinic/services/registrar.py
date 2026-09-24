import json
import os
import urllib.error
import urllib.request
from typing import Any


class RegistrarServiceError(Exception):
    """Base exception for Registrar integration errors."""


class RegistrarConnectionError(RegistrarServiceError):
    """Raised when the Registrar System cannot be reached."""


class RegistrarNotFoundError(RegistrarServiceError):
    """Raised when the requested student does not exist."""


class RegistrarService:
    """
    Service layer responsible for communication between the Clinic
    System and the external Registrar System.

    The Clinic backend should use this service instead of calling
    Registrar endpoints directly from views.
    """

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        timeout: int = 5,
    ):
        self.base_url = (
            base_url
            or os.getenv(
                "REGISTRAR_API_BASE_URL",
                "http://localhost:5000/api/v1",
            )
        ).rstrip("/")

        self.token = (
            token
            if token is not None
            else os.getenv("REGISTRAR_API_TOKEN", "")
        )

        self.timeout = timeout

    def _request(
        self,
        method: str,
        endpoint: str,
    ) -> dict[str, Any]:
        """
        Send an HTTP request to the Registrar System and return
        the decoded JSON response.
        """

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        headers = {
            "Accept": "application/json",
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        request = urllib.request.Request(
            url=url,
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

            if exc.code == 404:
                raise RegistrarNotFoundError(
                    error_data.get(
                        "message",
                        "Student was not found in the Registrar System.",
                    )
                ) from exc

            message = (
                error_data.get("message")
                or error_data.get("detail")
                or f"Registrar System returned HTTP {exc.code}."
            )

            raise RegistrarServiceError(message) from exc

        except (
            urllib.error.URLError,
            TimeoutError,
            ConnectionError,
        ) as exc:
            raise RegistrarConnectionError(
                "Unable to connect to the Registrar System."
            ) from exc

        try:
            result = json.loads(response_body)
        except json.JSONDecodeError as exc:
            raise RegistrarServiceError(
                "Registrar System returned an invalid JSON response."
            ) from exc

        if not isinstance(result, dict):
            raise RegistrarServiceError(
                "Registrar System returned an invalid response format."
            )

        return result

    def get_student(self, student_id: int) -> dict[str, Any]:
        """
        Retrieve a student from the Registrar System.

        Expected response:

        {
            "id": 24,
            "studentNumber": "2026-001",
            "firstName": "Juan",
            "lastName": "Dela Cruz",
            "email": "juan.delacruz@example.com",
            "program": "Bachelor of Science in Information Technology",
            "yearLevel": 3,
            "status": "Active"
        }
        """

        if student_id < 1:
            raise ValueError("student_id must be greater than 0.")

        result = self._request(
            method="GET",
            endpoint=f"/students/{student_id}",
        )

        required_fields = {
            "id",
            "studentNumber",
            "firstName",
            "lastName",
            "email",
            "program",
            "yearLevel",
            "status",
        }

        missing_fields = required_fields - result.keys()

        if missing_fields:
            raise RegistrarServiceError(
                "Registrar System returned an incomplete student response."
            )

        return result