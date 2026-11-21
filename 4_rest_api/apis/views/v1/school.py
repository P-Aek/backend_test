from django.db.models import Count
from rest_framework import viewsets

from apis.filters import ClassroomFilter, SchoolFilter
from apis.models import Classroom, School
from apis.serializers import (
    ClassroomDetailSerializer,
    ClassroomSerializer,
    SchoolDetailSerializer,
    SchoolSerializer,
)


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all().order_by("school_id")
    filterset_class = SchoolFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "retrieve":
            queryset = queryset.annotate(
                classroom_count=Count("classrooms", distinct=True),
                teacher_count=Count("classrooms__teachers", distinct=True),
                student_count=Count("classrooms__students", distinct=True),
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SchoolDetailSerializer
        return SchoolSerializer


class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.select_related("school").order_by("classroom_id")
    filterset_class = ClassroomFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "retrieve":
            queryset = queryset.prefetch_related("teachers", "students")
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ClassroomDetailSerializer
        return ClassroomSerializer
