from django.contrib import admin
from django.db import IntegrityError
from django.db.models import Count
from django.test import TestCase

from apis.admin import ClassroomAdmin, SchoolAdmin, StudentAdmin, TeacherAdmin
from apis.models import Classroom, Gender, School, Student, Teacher
from apis.serializers import (
    ClassroomDetailSerializer,
    ClassroomSerializer,
    SchoolDetailSerializer,
    SchoolSerializer,
    StudentDetailSerializer,
    StudentSerializer,
    TeacherDetailSerializer,
    TeacherSerializer,
)


class SchoolModelTests(TestCase):
    def test_create_school_and_str(self):
        school = School.objects.create(
            school_fullname="Bangkok Wittaya School",
            school_shortname="BWS",
            school_add="123 Sukhumvit Rd, Bangkok",
        )
        self.assertIsNotNone(school.school_id)
        self.assertEqual(str(school), "Bangkok Wittaya School")


class ClassroomModelTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            school_fullname="Bangkok Wittaya School",
            school_shortname="BWS",
            school_add="123 Sukhumvit Rd, Bangkok",
        )

    def test_create_classroom_and_str(self):
        classroom = Classroom.objects.create(
            classroom_year="M.1",
            classroom_tap="1",
            school=self.school,
        )
        self.assertIsNotNone(classroom.classroom_id)
        self.assertEqual(str(classroom), "BWS - M.1/1")

    def test_school_one_to_many_classrooms_and_cascade(self):
        c1 = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="1", school=self.school
        )
        c2 = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="2", school=self.school
        )
        self.assertEqual(self.school.classrooms.count(), 2)
        self.assertIn(c1, self.school.classrooms.all())
        self.assertIn(c2, self.school.classrooms.all())

        self.school.delete()
        self.assertEqual(Classroom.objects.count(), 0)


class TeacherModelTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            school_fullname="Bangkok Wittaya School",
            school_shortname="BWS",
            school_add="123 Sukhumvit Rd, Bangkok",
        )
        self.c1 = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="1", school=self.school
        )
        self.c2 = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="2", school=self.school
        )

    def test_create_teacher_and_str(self):
        teacher = Teacher.objects.create(
            teacher_firstname="Somchai",
            teacher_lastname="Jaidee",
            teacher_gender=Gender.MALE,
        )
        self.assertIsNotNone(teacher.teacher_id)
        self.assertEqual(str(teacher), "Somchai Jaidee")
        self.assertEqual(teacher.classrooms.count(), 0)

    def test_teacher_classroom_many_to_many(self):
        t1 = Teacher.objects.create(
            teacher_firstname="Somchai",
            teacher_lastname="Jaidee",
            teacher_gender=Gender.MALE,
        )
        t2 = Teacher.objects.create(
            teacher_firstname="Suda",
            teacher_lastname="Rakdee",
            teacher_gender=Gender.FEMALE,
        )

        # Multiple classrooms per teacher
        t1.classrooms.add(self.c1, self.c2)
        self.assertEqual(t1.classrooms.count(), 2)

        # Multiple teachers per classroom
        t2.classrooms.add(self.c1)
        self.assertEqual(self.c1.teachers.count(), 2)
        self.assertIn(t1, self.c1.teachers.all())
        self.assertIn(t2, self.c1.teachers.all())


class StudentModelTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            school_fullname="Bangkok Wittaya School",
            school_shortname="BWS",
            school_add="123 Sukhumvit Rd, Bangkok",
        )
        self.classroom = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="1", school=self.school
        )

    def test_create_student_and_str(self):
        student = Student.objects.create(
            student_firstname="Anan",
            student_lastname="Sukjai",
            student_gender=Gender.OTHER,
            classroom=self.classroom,
        )
        self.assertIsNotNone(student.student_id)
        self.assertEqual(str(student), "Anan Sukjai")

    def test_student_requires_classroom(self):
        with self.assertRaises(IntegrityError):
            Student.objects.create(
                student_firstname="Anan",
                student_lastname="Sukjai",
                student_gender=Gender.MALE,
                classroom=None,
            )

    def test_classroom_one_to_many_students_and_cascade(self):
        s1 = Student.objects.create(
            student_firstname="Anan",
            student_lastname="Sukjai",
            student_gender=Gender.MALE,
            classroom=self.classroom,
        )
        s2 = Student.objects.create(
            student_firstname="Malee",
            student_lastname="Deejai",
            student_gender=Gender.FEMALE,
            classroom=self.classroom,
        )
        self.assertEqual(self.classroom.students.count(), 2)
        self.assertIn(s1, self.classroom.students.all())
        self.assertIn(s2, self.classroom.students.all())

        self.classroom.delete()
        self.assertEqual(Student.objects.count(), 0)


class AdminRegistrationTests(TestCase):
    def test_models_registered_in_admin(self):
        self.assertTrue(admin.site.is_registered(School))
        self.assertTrue(admin.site.is_registered(Classroom))
        self.assertTrue(admin.site.is_registered(Teacher))
        self.assertTrue(admin.site.is_registered(Student))

        self.assertIsInstance(admin.site._registry[School], SchoolAdmin)
        self.assertIsInstance(admin.site._registry[Classroom], ClassroomAdmin)
        self.assertIsInstance(admin.site._registry[Teacher], TeacherAdmin)
        self.assertIsInstance(admin.site._registry[Student], StudentAdmin)


class SchoolSerializerTests(TestCase):
    def test_school_serializer_valid_create(self):
        payload = {
            "school_fullname": "Bangkok Wittaya School",
            "school_shortname": "BWS",
            "school_add": "123 Sukhumvit Rd, Bangkok",
        }
        serializer = SchoolSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        school = serializer.save()

        self.assertEqual(school.school_fullname, "Bangkok Wittaya School")
        self.assertEqual(
            set(serializer.data.keys()),
            {"school_id", "school_fullname", "school_shortname", "school_add"},
        )

    def test_school_detail_serializer_counts_distinct_teachers_and_isolates_school(self):
        school = School.objects.create(
            school_fullname="Bangkok Wittaya School",
            school_shortname="BWS",
            school_add="123 Sukhumvit Rd",
        )
        other_school = School.objects.create(
            school_fullname="Chiang Mai School",
            school_shortname="CMS",
            school_add="99 Nimman Rd",
        )

        c1 = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="1", school=school
        )
        c2 = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="2", school=school
        )
        other_c = Classroom.objects.create(
            classroom_year="M.2", classroom_tap="1", school=other_school
        )

        # Teacher assigned to 2 classrooms in the same school should be counted once
        t1 = Teacher.objects.create(
            teacher_firstname="Somchai",
            teacher_lastname="Jaidee",
            teacher_gender=Gender.MALE,
        )
        t1.classrooms.add(c1, c2)

        t2 = Teacher.objects.create(
            teacher_firstname="Suda",
            teacher_lastname="Rakdee",
            teacher_gender=Gender.FEMALE,
        )
        t2.classrooms.add(c2)

        other_t = Teacher.objects.create(
            teacher_firstname="Narin",
            teacher_lastname="North",
            teacher_gender=Gender.OTHER,
        )
        other_t.classrooms.add(other_c)

        Student.objects.create(
            student_firstname="Anan",
            student_lastname="Sukjai",
            student_gender=Gender.MALE,
            classroom=c1,
        )
        Student.objects.create(
            student_firstname="Malee",
            student_lastname="Deejai",
            student_gender=Gender.FEMALE,
            classroom=c2,
        )
        Student.objects.create(
            student_firstname="Kanya",
            student_lastname="Other",
            student_gender=Gender.FEMALE,
            classroom=other_c,
        )

        data = SchoolDetailSerializer(school).data
        self.assertEqual(data["school_id"], school.school_id)
        self.assertEqual(data["classroom_count"], 2)
        self.assertEqual(data["teacher_count"], 2)
        self.assertEqual(data["student_count"], 2)

        annotated_school = (
            School.objects.filter(pk=school.pk)
            .annotate(
                classroom_count=Count("classrooms", distinct=True),
                teacher_count=Count("classrooms__teachers", distinct=True),
                student_count=Count("classrooms__students", distinct=True),
            )
            .get()
        )
        annotated_data = SchoolDetailSerializer(annotated_school).data
        self.assertEqual(annotated_data["classroom_count"], 2)
        self.assertEqual(annotated_data["teacher_count"], 2)
        self.assertEqual(annotated_data["student_count"], 2)


class ClassroomSerializerTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            school_fullname="Bangkok Wittaya School",
            school_shortname="BWS",
            school_add="123 Sukhumvit Rd",
        )

    def test_classroom_serializer_valid_create(self):
        payload = {
            "classroom_year": "M.1",
            "classroom_tap": "1",
            "school": self.school.school_id,
        }
        serializer = ClassroomSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        classroom = serializer.save()

        self.assertEqual(classroom.school, self.school)
        self.assertEqual(
            set(serializer.data.keys()),
            {"classroom_id", "classroom_year", "classroom_tap", "school"},
        )

    def test_classroom_detail_serializer_nested_teachers_and_students(self):
        classroom = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="1", school=self.school
        )
        teacher = Teacher.objects.create(
            teacher_firstname="Somchai",
            teacher_lastname="Jaidee",
            teacher_gender=Gender.MALE,
        )
        teacher.classrooms.add(classroom)

        student = Student.objects.create(
            student_firstname="Anan",
            student_lastname="Sukjai",
            student_gender=Gender.MALE,
            classroom=classroom,
        )

        data = ClassroomDetailSerializer(classroom).data
        self.assertEqual(data["classroom_id"], classroom.classroom_id)
        self.assertEqual(len(data["teachers"]), 1)
        self.assertEqual(
            data["teachers"][0],
            {
                "teacher_id": teacher.teacher_id,
                "teacher_firstname": "Somchai",
                "teacher_lastname": "Jaidee",
                "teacher_gender": Gender.MALE,
            },
        )
        self.assertEqual(len(data["students"]), 1)
        self.assertEqual(
            data["students"][0],
            {
                "student_id": student.student_id,
                "student_firstname": "Anan",
                "student_lastname": "Sukjai",
                "student_gender": Gender.MALE,
            },
        )


class TeacherSerializerTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            school_fullname="Bangkok Wittaya School",
            school_shortname="BWS",
            school_add="123 Sukhumvit Rd",
        )
        self.c1 = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="1", school=self.school
        )
        self.c2 = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="2", school=self.school
        )

    def test_teacher_serializer_create_with_multiple_classrooms(self):
        payload = {
            "teacher_firstname": "Somchai",
            "teacher_lastname": "Jaidee",
            "teacher_gender": Gender.MALE,
            "classrooms": [self.c1.classroom_id, self.c2.classroom_id],
        }
        serializer = TeacherSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        teacher = serializer.save()

        self.assertEqual(teacher.classrooms.count(), 2)
        self.assertEqual(
            set(serializer.data["classrooms"]),
            {self.c1.classroom_id, self.c2.classroom_id},
        )

    def test_teacher_serializer_create_with_empty_or_omitted_classrooms(self):
        empty_serializer = TeacherSerializer(
            data={
                "teacher_firstname": "Suda",
                "teacher_lastname": "Rakdee",
                "teacher_gender": Gender.FEMALE,
                "classrooms": [],
            }
        )
        self.assertTrue(empty_serializer.is_valid(), empty_serializer.errors)
        t_empty = empty_serializer.save()
        self.assertEqual(t_empty.classrooms.count(), 0)

        omitted_serializer = TeacherSerializer(
            data={
                "teacher_firstname": "Narin",
                "teacher_lastname": "Suk",
                "teacher_gender": Gender.OTHER,
            }
        )
        self.assertTrue(omitted_serializer.is_valid(), omitted_serializer.errors)
        t_omitted = omitted_serializer.save()
        self.assertEqual(t_omitted.classrooms.count(), 0)

    def test_teacher_serializer_rejects_invalid_gender(self):
        serializer = TeacherSerializer(
            data={
                "teacher_firstname": "Somchai",
                "teacher_lastname": "Jaidee",
                "teacher_gender": "invalid_gender",
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("teacher_gender", serializer.errors)

    def test_teacher_detail_serializer_nested_classrooms(self):
        teacher = Teacher.objects.create(
            teacher_firstname="Somchai",
            teacher_lastname="Jaidee",
            teacher_gender=Gender.MALE,
        )
        teacher.classrooms.add(self.c1, self.c2)

        data = TeacherDetailSerializer(teacher).data
        self.assertEqual(data["teacher_id"], teacher.teacher_id)
        self.assertEqual(len(data["classrooms"]), 2)
        self.assertEqual(
            {c["classroom_id"] for c in data["classrooms"]},
            {self.c1.classroom_id, self.c2.classroom_id},
        )
        self.assertEqual(
            set(data["classrooms"][0].keys()),
            {"classroom_id", "classroom_year", "classroom_tap", "school"},
        )


class StudentSerializerTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            school_fullname="Bangkok Wittaya School",
            school_shortname="BWS",
            school_add="123 Sukhumvit Rd",
        )
        self.classroom = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="1", school=self.school
        )

    def test_student_serializer_create_with_required_classroom(self):
        payload = {
            "student_firstname": "Anan",
            "student_lastname": "Sukjai",
            "student_gender": Gender.MALE,
            "classroom": self.classroom.classroom_id,
        }
        serializer = StudentSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        student = serializer.save()

        self.assertEqual(student.classroom, self.classroom)
        self.assertEqual(
            set(serializer.data.keys()),
            {
                "student_id",
                "student_firstname",
                "student_lastname",
                "student_gender",
                "classroom",
            },
        )

    def test_student_serializer_rejects_missing_classroom(self):
        serializer = StudentSerializer(
            data={
                "student_firstname": "Anan",
                "student_lastname": "Sukjai",
                "student_gender": Gender.MALE,
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("classroom", serializer.errors)

    def test_student_serializer_rejects_invalid_gender(self):
        serializer = StudentSerializer(
            data={
                "student_firstname": "Anan",
                "student_lastname": "Sukjai",
                "student_gender": "unknown",
                "classroom": self.classroom.classroom_id,
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("student_gender", serializer.errors)

    def test_student_detail_serializer_nested_classroom(self):
        student = Student.objects.create(
            student_firstname="Anan",
            student_lastname="Sukjai",
            student_gender=Gender.MALE,
            classroom=self.classroom,
        )
        data = StudentDetailSerializer(student).data
        self.assertEqual(data["student_id"], student.student_id)
        self.assertEqual(
            data["classroom"],
            {
                "classroom_id": self.classroom.classroom_id,
                "classroom_year": "M.1",
                "classroom_tap": "1",
                "school": self.school.school_id,
            },
        )
