from django.contrib import admin

from apis.models import Classroom, School, Student, Teacher


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ("school_id", "school_fullname", "school_shortname", "school_add")
    search_fields = ("school_fullname", "school_shortname")


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ("classroom_id", "school", "classroom_year", "classroom_tap")
    list_filter = ("school",)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("teacher_id", "teacher_firstname", "teacher_lastname", "teacher_gender")
    list_filter = ("teacher_gender",)
    search_fields = ("teacher_firstname", "teacher_lastname")
    filter_horizontal = ("classrooms",)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "student_id",
        "student_firstname",
        "student_lastname",
        "student_gender",
        "classroom",
    )
    list_filter = ("student_gender", "classroom", "classroom__school")
    search_fields = ("student_firstname", "student_lastname")
