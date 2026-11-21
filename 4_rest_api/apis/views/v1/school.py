from rest_framework import viewsets

from apis.filters import SchoolFilter
from apis.models import School
from apis.serializers import SchoolDetailSerializer, SchoolSerializer
from apis.views.v1 import ActionSerializerMixin


class SchoolViewSet(ActionSerializerMixin, viewsets.ModelViewSet):
    queryset = School.objects.all().order_by("school_id")
    serializer_class = SchoolSerializer
    detail_serializer_class = SchoolDetailSerializer
    filterset_class = SchoolFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "retrieve":
            queryset = queryset.with_counts()
        return queryset
