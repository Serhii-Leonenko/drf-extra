# Usage

## Action-based serializers for ViewSets

Each action can have a separate serializer:

```python
from drf_extra.mixins import RetrieveModelMixin, ListModelMixin
from drf_extra.viewsets import GenericViewSet
...

class OrderViewSet(
    RetrieveModelMixin,
    ListModelMixin,
    GenericViewSet
):
    response_action_serializer_classes = {
        "retrieve": OrderSerializer,
        "list": OrderListSerializer,
    }
```

## Two serializers per request/response cycle

We found that more often than not we need a separate serializer for handling request payload and a separate serializer for generating response data.

How to achieve it in ViewSet:

```python
from drf_extra.mixins import CreateModelMixin, ListModelMixin
from drf_extra.viewsets import GenericViewSet
...

class OrderViewSet(
    CreateModelMixin,
    ListModelMixin,
    GenericViewSet
):
    request_action_serializer_classes = {
        "create": OrderCreateSerializer,
    }
    response_action_serializer_classes = {
        "create": OrderResponseSerializer,
        "list": OrderResponseSerializer,
        "cancel": OrderResponseSerializer,
    }
```

How to achieve it in GenericAPIView:

```python
from drf_extra.generics import CreateAPIView
...


class OrderCreateView(CreateAPIView):
    request_serializer_class = OrderCreateSerializer
    response_serializer_class = OrderResponseSerializer
```

## Action-based permissions for ViewSets

Each action can have a separate set of permissions:

```python
from drf_extra.mixins import CreateModelMixin, UpdateModelMixin, ListModelMixin
from drf_extra.viewsets import GenericViewSet
from drf_extra.permissions import AllowAny, IsAuthenticated
...

class OrderViewSet(
    CreateModelMixin,
    UpdateModelMixin,
    ListModelMixin,
    GenericViewSet
):
    action_permission_classes = {
        "create": IsAuthenticated,
        "update": [IsAuthenticated, IsOrderOwner],
        "list": AllowAny,
    }
```

## Single format for all errors

We believe that having a single format for all errors is good practice. This will make the process of displaying and handling errors much simpler for clients that use your APIs.

Any error always will be a JSON object with a message, code (identifier of the error), and field if the error is specific to a particular field. How your response could look like:

```python
{
    "errors": [
        {
            "message": "Delete or cancel all reservations first.",
            "code": "invalid"
        },
        {
            "message": "Ensure this field has no more than 21 characters.",
            "code": "max_length",
            "field": "address.work_phone"
        },
        {
            "message": "This email already exists",
            "code": "unique",
            "field": "login_email"
        }
    ]
}
```

You will not have a single format out-of-the-box after installation. You need to add an exception handler to your DRF settings:

```python
REST_FRAMEWORK = {
    ...
    "EXCEPTION_HANDLER": "drf_extra.exception_handlers.errors_formatter_exception_handler",
}
```

## OpenAPI for request and response serializers for drf_spectacular

If you use `drf_spectacular` for generating OpenAPI schema, you can use `RequestResponseAutoSchema` to generate schema for request and response serializers.

```python
...
SPECTACULAR_SETTINGS = {
    ...
    "DEFAULT_SCHEMA_CLASS": "drf_extra.openapi.RequestResponseAutoSchema",
}
```

## Authentication backend for email or username

If you want to authenticate users with email or username, you can use `EmailOrUsernameModelBackend` authentication backend.

```python
...
AUTHENTICATION_BACKENDS = [
    "drf_extra.auth_backend.EmailOrUsernameModelBackend",
]
```
