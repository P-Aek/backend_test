from rest_framework import viewsets

from apis.filters import StudentFilter
from apis.models import Student
from apis.serializers import StudentDetailSerializer, StudentSerializer
from apis.views.v1 import ActionSerializerMixin


class StudentViewSet(ActionSerializerMixin, viewsets.ModelViewSet):
    queryset = Student.objects.select_related("classroom", "classroom__school").order_by(
        "student_id"
    )
    serializer_class = StudentSerializer
    detail_serializer_class = StudentDetailSerializer
    filterset_class = StudentFilter
