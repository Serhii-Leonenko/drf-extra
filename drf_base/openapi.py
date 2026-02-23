from typing import Optional, Type, Union

from django.core.exceptions import ImproperlyConfigured
from drf_spectacular.openapi import AutoSchema
from rest_framework.serializers import Serializer


class RequestResponseAutoSchema(AutoSchema):
    def get_request_serializer(self) -> Optional[Union[Serializer, Type[Serializer]]]:
        if request_serializer := getattr(self.view, "get_request_serializer", None):

            try:
                return request_serializer()
            except ImproperlyConfigured:
                pass

        return self._get_serializer()

    def get_response_serializers(self) -> Optional[Union[Serializer, Type[Serializer]]]:
        if response_serializer := getattr(self.view, "get_response_serializer", None):

            try:
                return response_serializer()
            except ImproperlyConfigured:
                pass

        return self._get_serializer()
