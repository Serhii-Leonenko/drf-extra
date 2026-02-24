from rest_framework import views

from drf_extra.mixins import DjangoValidationErrorTransformMixin


class APIView(DjangoValidationErrorTransformMixin, views.APIView):
    pass
