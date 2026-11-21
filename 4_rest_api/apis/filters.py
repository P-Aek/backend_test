from django.db.models import Q
from django_filters import FilterSet, filters

from apis.models import Classroom, Gender, School, Student, Teacher


class SchoolFilter(FilterSet):
    name = filters.CharFilter(method="filter_name")

    class Meta:
        model = School
        fields = ("name",)

    def filter_name(self, queryset, name, value):
        return queryset.filter(
            Q(school_fullname__icontains=value) | Q(school_shortname__icontains=value)
        )


class ClassroomFilter(FilterSet):
    school = filters.NumberFilter(field_name="school_id")

    class Meta:
        model = Classroom
        fields = ("school",)


class TeacherFilter(FilterSet):
    school = filters.NumberFilter(field_name="classrooms__school_id", distinct=True)
    classroom = filters.NumberFilter(
        field_name="classrooms__classroom_id", distinct=True
    )
    firstname = filters.CharFilter(
        field_name="teacher_firstname", lookup_expr="icontains"
    )
    lastname = filters.CharFilter(
        field_name="teacher_lastname", lookup_expr="icontains"
    )
    gender = filters.ChoiceFilter(field_name="teacher_gender", choices=Gender.choices)

    class Meta:
        model = Teacher
        fields = ("school", "classroom", "firstname", "lastname", "gender")


class StudentFilter(FilterSet):
    school = filters.NumberFilter(field_name="classroom__school_id")
    classroom = filters.NumberFilter(field_name="classroom_id")
    firstname = filters.CharFilter(
        field_name="student_firstname", lookup_expr="icontains"
    )
    lastname = filters.CharFilter(
        field_name="student_lastname", lookup_expr="icontains"
    )
    gender = filters.ChoiceFilter(field_name="student_gender", choices=Gender.choices)

    class Meta:
        model = Student
        fields = ("school", "classroom", "firstname", "lastname", "gender")
