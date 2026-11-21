from rest_framework import serializers

from apis.models import Classroom, School, Student, Teacher


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ["school_id", "school_fullname", "school_shortname", "school_add"]


class SchoolDetailSerializer(SchoolSerializer):
    classroom_count = serializers.SerializerMethodField()
    teacher_count = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()

    class Meta(SchoolSerializer.Meta):
        fields = [
            *SchoolSerializer.Meta.fields,
            "classroom_count",
            "teacher_count",
            "student_count",
        ]

    def get_classroom_count(self, obj):
        count = getattr(obj, "classroom_count", None)
        if count is not None:
            return count
        return obj.classrooms.count()

    def get_teacher_count(self, obj):
        count = getattr(obj, "teacher_count", None)
        if count is not None:
            return count
        return Teacher.objects.filter(classrooms__school=obj).distinct().count()

    def get_student_count(self, obj):
        count = getattr(obj, "student_count", None)
        if count is not None:
            return count
        return Student.objects.filter(classroom__school=obj).count()


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


class TeacherDetailSerializer(TeacherSerializer):
    classrooms = ClassroomSerializer(many=True, read_only=True)

    class Meta(TeacherSerializer.Meta):
        fields = [*TeacherSerializer.Meta.fields]


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


class StudentDetailSerializer(StudentSerializer):
    classroom = ClassroomSerializer(read_only=True)

    class Meta(StudentSerializer.Meta):
        fields = [*StudentSerializer.Meta.fields]
