from django.core import exceptions as django_exceptions
from PIL import Image
from rest_framework import exceptions as rest_exceptions
from rest_framework import status
from rest_framework.fields import get_error_detail
from rest_framework.mixins import ListModelMixin as DRFListModelMixin
from rest_framework.response import Response


class DjangoValidationErrorTransformMixin:
    """
    Transforms Django's ValidationError into REST Framework's ValidationError.
    Without this mixin, server responds with 500 status code which is not desired.
    """

    def handle_exception(self, exc):
        if isinstance(exc, django_exceptions.ValidationError):
            drf_exception = rest_exceptions.ValidationError(get_error_detail(exc))
            return super().handle_exception(drf_exception)

        return super().handle_exception(exc)


class CreateModelMixin:
    """
    Create a model instance.
    """

    def create(self, request, *_args, **_kwargs):
        request_serializer = self.get_request_serializer(data=request.data)

        request_serializer.is_valid(raise_exception=True)

        instance = self.perform_create(request_serializer)
        response_serializer = self.get_response_serializer(instance)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        return serializer.save()


class RetrieveModelMixin:
    """
    Retrieve a model instance.
    """

    def retrieve(self, _request, *_args, **_kwargs):
        instance = self.get_object()
        serializer = self.get_response_serializer(instance)

        return Response(serializer.data)


class ListModelMixin(DRFListModelMixin):
    """
    List a queryset.
    """

    def list(self, _request, *_args, **_kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_response_serializer(page, many=True)

            return self.get_paginated_response(serializer.data)

        serializer = self.get_response_serializer(queryset, many=True)

        return Response(serializer.data)


class _UpdateMixin:
    def _update(self, request, *_args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        request_serializer = self.get_request_serializer(
            instance, data=request.data, partial=partial
        )
        request_serializer.is_valid(raise_exception=True)

        if partial:
            instance = self.perform_partial_update(instance, request_serializer)
        else:
            instance = self.perform_update(instance, request_serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        response_serializer = self.get_response_serializer(instance)

        return Response(response_serializer.data)

    def perform_update(self, instance, serializer):
        return serializer.save()

    def perform_partial_update(self, instance, serializer):
        return self.perform_update(instance, serializer)


class UpdateModelMixin(_UpdateMixin):
    """
    Update a model instance.
    """

    def update(self, *args, **kwargs):
        return self._update(*args, **kwargs)

    def partial_update(self, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(*args, **kwargs)


class FullUpdateModelMixin(_UpdateMixin):
    """
    Fully update a model instance.
    """

    def update(self, *args, **kwargs):
        return self._update(*args, **kwargs)


class PartialUpdateModelMixin(_UpdateMixin):
    """
    Partially update a model instance.
    """

    def partial_update(self, *args, **kwargs):
        kwargs["partial"] = True
        return self._update(*args, **kwargs)


class DestroyModelMixin:
    """
    Destroy a model instance.
    """

    def destroy(self, request, *_args, **_kwargs):
        instance = self.get_object()
        serializer = self.get_request_serializer_or_none(instance, data=request.data)

        if serializer is not None:
            serializer.is_valid(raise_exception=True)
            self.perform_destroy(instance, serializer)
        else:
            self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance, serializer=None):
        instance.delete()


class ThumbnailMixin:
    """
    Add method for creating thumbnails
    """

    def make_thumbnail(self, img: Image) -> Image:
        """
        Crop and resize the image for thumbnail

        Args:
            img:

        Returns:
            Image
        """
        target_width, target_height = self.THUMBNAIL_SIZE
        source_width, source_height = img.size
        source_aspect = source_width / source_height
        target_aspect = target_width / target_height

        if source_aspect > target_aspect:
            new_width = int(source_height * target_aspect)
            offset = (source_width - new_width) // 2
            box = (offset, 0, offset + new_width, source_height)
        else:
            new_height = int(source_width / target_aspect)
            offset = (source_height - new_height) // 2
            box = (0, offset, source_width, offset + new_height)

        img = img.crop(box)
        img.thumbnail(self.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)

        return img
