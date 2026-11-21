from rest_framework import serializers

from apis.models import Classroom, School, Student, Teacher


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ["school_id", "school_fullname", "school_shortname", "school_add"]


class SchoolDetailSerializer(SchoolSerializer):
    classroom_count = serializers.IntegerField(read_only=True)
    teacher_count = serializers.IntegerField(read_only=True)
    student_count = serializers.IntegerField(read_only=True)

    class Meta(SchoolSerializer.Meta):
        fields = [
            *SchoolSerializer.Meta.fields,
            "classroom_count",
            "teacher_count",
            "student_count",
        ]
        read_only_fields = fields


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ["classroom_id", "classroom_year", "classroom_tap", "school"]


class TeacherSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = [
            "teacher_id",
            "teacher_firstname",
            "teacher_lastname",
            "teacher_gender",
        ]


class StudentSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "student_id",
            "student_firstname",
            "student_lastname",
            "student_gender",
        ]


class ClassroomDetailSerializer(ClassroomSerializer):
    teachers = TeacherSummarySerializer(many=True, read_only=True)
    students = StudentSummarySerializer(many=True, read_only=True)

    class Meta(ClassroomSerializer.Meta):
        fields = [*ClassroomSerializer.Meta.fields, "teachers", "students"]


class TeacherSerializer(serializers.ModelSerializer):
    classrooms = serializers.PrimaryKeyRelatedField(
        queryset=Classroom.objects.all(), many=True, required=False
    )

    class Meta:
        model = Teacher
        fields = [
            "teacher_id",
            "teacher_firstname",
            "teacher_lastname",
            "teacher_gender",
            "classrooms",
        ]


class TeacherDetailSerializer(serializers.ModelSerializer):
    classrooms = ClassroomSerializer(many=True, read_only=True)

    class Meta:
        model = Teacher
        fields = [
            "teacher_id",
            "teacher_firstname",
            "teacher_lastname",
            "teacher_gender",
            "classrooms",
        ]
        read_only_fields = fields


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "student_id",
            "student_firstname",
            "student_lastname",
            "student_gender",
            "classroom",
        ]


class StudentDetailSerializer(serializers.ModelSerializer):
    classroom = ClassroomSerializer(read_only=True)

    class Meta:
        model = Student
        fields = [
            "student_id",
            "student_firstname",
            "student_lastname",
            "student_gender",
            "classroom",
        ]
        read_only_fields = fields
