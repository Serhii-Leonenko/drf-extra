from django_filters.rest_framework import DjangoFilterBackend


class FilterBackend(DjangoFilterBackend):
    """
    Custom filter backend to support filtering by action.
    """

    def get_filterset_class(self, view, queryset=None):
        """
        Look for an 'action_filtersets' attribute on the view and use the filterset_class
        """
        filterset_class = getattr(view, "filterset_class", None)
        filterset_fields = getattr(view, "filterset_fields", None)
        action_filterset_classes = getattr(view, "action_filterset_classes", None)

        if action_filterset_classes and view.action in action_filterset_classes:
            filterset_class = action_filterset_classes[view.action]

        if filterset_class:
            filterset_model = filterset_class._meta.model

            if filterset_model and queryset is not None:
                assert issubclass(
                    queryset.model, filterset_model
                ), "FilterSet model %s does not match queryset model %s" % (
                    filterset_model,
                    queryset.model,
                )

            return filterset_class

        if filterset_fields and queryset is not None:
            MetaBase = getattr(self.filterset_base, "Meta", object)

            class AutoFilterSet(self.filterset_base):
                class Meta(MetaBase):
                    model = queryset.model
                    fields = filterset_fields

            return AutoFilterSet

        return None
