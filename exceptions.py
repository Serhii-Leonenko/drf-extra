from rest_framework.exceptions import APIException


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = "Service temporarily unavailable, try again later."
    default_code = "service_unavailable"


class ConflictError(APIException):
    status_code = 409
    default_detail = "Conflict."
    default_code = "conflict"
