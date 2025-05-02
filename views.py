from rest_framework import views

from base.mixins import DjangoValidationErrorTransformMixin


class APIView(DjangoValidationErrorTransformMixin, views.APIView):
    pass
