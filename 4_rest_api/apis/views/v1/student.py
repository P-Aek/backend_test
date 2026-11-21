from rest_framework import viewsets

from apis.filters import StudentFilter
from apis.models import Student
from apis.serializers import StudentDetailSerializer, StudentSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related("classroom", "classroom__school").order_by(
        "student_id"
    )
    filterset_class = StudentFilter

    def get_serializer_class(self):
        if self.action == "retrieve":
            return StudentDetailSerializer
        return StudentSerializer
