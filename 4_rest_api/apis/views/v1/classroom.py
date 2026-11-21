from rest_framework import viewsets

from apis.filters import ClassroomFilter
from apis.models import Classroom
from apis.serializers import ClassroomDetailSerializer, ClassroomSerializer
from apis.views.v1 import ActionSerializerMixin


class ClassroomViewSet(ActionSerializerMixin, viewsets.ModelViewSet):
    queryset = Classroom.objects.select_related("school").order_by("classroom_id")
    serializer_class = ClassroomSerializer
    detail_serializer_class = ClassroomDetailSerializer
    filterset_class = ClassroomFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "retrieve":
            queryset = queryset.prefetch_related("teachers", "students")
        return queryset
