from rest_framework import viewsets

from apis.filters import TeacherFilter
from apis.models import Teacher
from apis.serializers import TeacherDetailSerializer, TeacherSerializer
from apis.views.v1 import ActionSerializerMixin


class TeacherViewSet(ActionSerializerMixin, viewsets.ModelViewSet):
    queryset = Teacher.objects.prefetch_related("classrooms").order_by("teacher_id")
    serializer_class = TeacherSerializer
    detail_serializer_class = TeacherDetailSerializer
    filterset_class = TeacherFilter
