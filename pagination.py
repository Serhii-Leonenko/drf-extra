from rest_framework.pagination import LimitOffsetPagination


class HundredMaxLimitOffsetPagination(LimitOffsetPagination):
    """
    Pagination class for limiting the number of objects in a single response.
    The default limit is 100, and the maximum limit is 100.
    """

    default_limit = 20
    max_limit = 100
