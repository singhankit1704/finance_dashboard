from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """Custom exception handler for consistent error response format."""
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {
            "success": False,
            "message": "An error occurred.",
            "errors": response.data,
        }

        # Make message human-readable for common cases
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            error_data["message"] = "Authentication required. Please provide a valid token."
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            error_data["message"] = str(exc.detail) if hasattr(exc, 'detail') else "You do not have permission."
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            error_data["message"] = "The requested resource was not found."
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            error_data["message"] = "Invalid input. Please check the submitted data."

        response.data = error_data

    return response
