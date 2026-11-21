from django.db import models
from django.db.models import Count


class Gender(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    OTHER = "other", "Other"


class SchoolQuerySet(models.QuerySet):
    def with_counts(self):
        return self.annotate(
            classroom_count=Count("classrooms", distinct=True),
            teacher_count=Count("classrooms__teachers", distinct=True),
            student_count=Count("classrooms__students", distinct=True),
        )


class School(models.Model):
    school_id = models.BigAutoField(primary_key=True)
    school_fullname = models.CharField(max_length=255)
    school_shortname = models.CharField(max_length=50)
    school_add = models.TextField()

    objects = SchoolQuerySet.as_manager()

    def __str__(self):
        return self.school_fullname


class Classroom(models.Model):
    classroom_id = models.BigAutoField(primary_key=True)
    classroom_year = models.CharField(max_length=50)
    classroom_tap = models.CharField(max_length=50)
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="classrooms"
    )

    def __str__(self):
        return f"{self.school.school_shortname} - {self.classroom_year}/{self.classroom_tap}"


class Teacher(models.Model):
    teacher_id = models.BigAutoField(primary_key=True)
    teacher_firstname = models.CharField(max_length=100)
    teacher_lastname = models.CharField(max_length=100)
    teacher_gender = models.CharField(max_length=20, choices=Gender.choices)
    classrooms = models.ManyToManyField(
        Classroom, related_name="teachers", blank=True
    )

    def __str__(self):
        return f"{self.teacher_firstname} {self.teacher_lastname}"


class Student(models.Model):
    student_id = models.BigAutoField(primary_key=True)
    student_firstname = models.CharField(max_length=100)
    student_lastname = models.CharField(max_length=100)
    student_gender = models.CharField(max_length=20, choices=Gender.choices)
    classroom = models.ForeignKey(
        Classroom, on_delete=models.CASCADE, related_name="students"
    )

    def __str__(self):
        return f"{self.student_firstname} {self.student_lastname}"
