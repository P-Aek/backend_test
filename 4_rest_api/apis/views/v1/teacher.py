from rest_framework import viewsets

from apis.filters import TeacherFilter
from apis.models import Teacher
from apis.serializers import TeacherDetailSerializer, TeacherSerializer


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.prefetch_related("classrooms").order_by("teacher_id")
    filterset_class = TeacherFilter

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TeacherDetailSerializer
        return TeacherSerializer
