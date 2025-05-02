from rest_framework.exceptions import ErrorDetail, Throttled
from rest_framework.views import exception_handler

from base.errors_formatter import ErrorsFormatter


def errors_formatter_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # If unexpected error occurs (server error, etc.)
    if response is None:
        return response

    # Change the default throttle message
    if isinstance(exc, Throttled):
        exc.detail = ErrorDetail(
            "Request limit exceeded, try again later", code=exc.detail.code
        )

    formatter = ErrorsFormatter(exc)
    response.data = formatter()

    return response
