from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import Count
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from apis.admin import ClassroomAdmin, SchoolAdmin, StudentAdmin, TeacherAdmin
from apis.filters import (
    ClassroomFilter,
    SchoolFilter,
    StudentFilter,
    TeacherFilter,
)
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


class SchoolFilterTests(TestCase):
    def setUp(self):
        self.s1 = School.objects.create(
            school_fullname="Bangkok Wittaya School",
            school_shortname="BWS",
            school_add="123 Sukhumvit Rd",
        )
        self.s2 = School.objects.create(
            school_fullname="Chiang Mai International Academy",
            school_shortname="CMIA",
            school_add="99 Nimman Rd",
        )

    def test_filter_by_partial_fullname_case_insensitive(self):
        qs = SchoolFilter({"name": "wittaya"}, queryset=School.objects.all()).qs
        self.assertEqual(list(qs), [self.s1])

    def test_filter_by_partial_shortname_case_insensitive(self):
        qs = SchoolFilter({"name": "cmi"}, queryset=School.objects.all()).qs
        self.assertEqual(list(qs), [self.s2])

    def test_filter_by_non_matching_name_returns_empty(self):
        qs = SchoolFilter({"name": "NonExistent"}, queryset=School.objects.all()).qs
        self.assertEqual(list(qs), [])


class ClassroomFilterTests(TestCase):
    def setUp(self):
        self.s1 = School.objects.create(
            school_fullname="Bangkok Wittaya School",
            school_shortname="BWS",
            school_add="123 Sukhumvit Rd",
        )
        self.s2 = School.objects.create(
            school_fullname="Chiang Mai School",
            school_shortname="CMS",
            school_add="99 Nimman Rd",
        )
        self.c1 = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="1", school=self.s1
        )
        self.c2 = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="2", school=self.s1
        )
        self.c3 = Classroom.objects.create(
            classroom_year="M.2", classroom_tap="1", school=self.s2
        )

    def test_filter_by_school_id(self):
        qs = ClassroomFilter(
            {"school": self.s1.school_id}, queryset=Classroom.objects.all()
        ).qs
        self.assertEqual(set(qs), {self.c1, self.c2})

        qs_other = ClassroomFilter(
            {"school": self.s2.school_id}, queryset=Classroom.objects.all()
        ).qs
        self.assertEqual(list(qs_other), [self.c3])


class TeacherFilterTests(TestCase):
    def setUp(self):
        self.s1 = School.objects.create(
            school_fullname="Bangkok Wittaya School",
            school_shortname="BWS",
            school_add="123 Sukhumvit Rd",
        )
        self.s2 = School.objects.create(
            school_fullname="Chiang Mai School",
            school_shortname="CMS",
            school_add="99 Nimman Rd",
        )
        self.c1 = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="1", school=self.s1
        )
        self.c2 = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="2", school=self.s1
        )
        self.c3 = Classroom.objects.create(
            classroom_year="M.2", classroom_tap="1", school=self.s2
        )

        # Teacher assigned to 2 classrooms in the same school
        self.t1 = Teacher.objects.create(
            teacher_firstname="Somchai",
            teacher_lastname="Jaidee",
            teacher_gender=Gender.MALE,
        )
        self.t1.classrooms.add(self.c1, self.c2)

        self.t2 = Teacher.objects.create(
            teacher_firstname="Suda",
            teacher_lastname="Rakdee",
            teacher_gender=Gender.FEMALE,
        )
        self.t2.classrooms.add(self.c2)

        self.t3 = Teacher.objects.create(
            teacher_firstname="Narin",
            teacher_lastname="Jaidee",
            teacher_gender=Gender.OTHER,
        )
        self.t3.classrooms.add(self.c3)

    def test_filter_by_school_returns_distinct_teachers(self):
        qs = TeacherFilter(
            {"school": self.s1.school_id}, queryset=Teacher.objects.all()
        ).qs
        result = list(qs)
        self.assertEqual(len(result), 2)
        self.assertEqual(set(result), {self.t1, self.t2})

    def test_filter_by_classroom(self):
        qs = TeacherFilter(
            {"classroom": self.c1.classroom_id}, queryset=Teacher.objects.all()
        ).qs
        self.assertEqual(list(qs), [self.t1])

    def test_filter_by_firstname_and_lastname(self):
        qs_first = TeacherFilter(
            {"firstname": "som"}, queryset=Teacher.objects.all()
        ).qs
        self.assertEqual(list(qs_first), [self.t1])

        qs_last = TeacherFilter(
            {"lastname": "jaidee"}, queryset=Teacher.objects.all()
        ).qs
        self.assertEqual(set(qs_last), {self.t1, self.t3})

    def test_filter_by_gender(self):
        qs = TeacherFilter(
            {"gender": Gender.FEMALE}, queryset=Teacher.objects.all()
        ).qs
        self.assertEqual(list(qs), [self.t2])

    def test_combined_filters(self):
        qs = TeacherFilter(
            {
                "school": self.s1.school_id,
                "lastname": "jaidee",
                "gender": Gender.MALE,
            },
            queryset=Teacher.objects.all(),
        ).qs
        self.assertEqual(list(qs), [self.t1])


class StudentFilterTests(TestCase):
    def setUp(self):
        self.s1 = School.objects.create(
            school_fullname="Bangkok Wittaya School",
            school_shortname="BWS",
            school_add="123 Sukhumvit Rd",
        )
        self.s2 = School.objects.create(
            school_fullname="Chiang Mai School",
            school_shortname="CMS",
            school_add="99 Nimman Rd",
        )
        self.c1 = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="1", school=self.s1
        )
        self.c2 = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="2", school=self.s1
        )
        self.c3 = Classroom.objects.create(
            classroom_year="M.2", classroom_tap="1", school=self.s2
        )

        self.st1 = Student.objects.create(
            student_firstname="Anan",
            student_lastname="Sukjai",
            student_gender=Gender.MALE,
            classroom=self.c1,
        )
        self.st2 = Student.objects.create(
            student_firstname="Malee",
            student_lastname="Deejai",
            student_gender=Gender.FEMALE,
            classroom=self.c2,
        )
        self.st3 = Student.objects.create(
            student_firstname="Ananya",
            student_lastname="Sukjai",
            student_gender=Gender.FEMALE,
            classroom=self.c3,
        )

    def test_filter_by_school(self):
        qs = StudentFilter(
            {"school": self.s1.school_id}, queryset=Student.objects.all()
        ).qs
        self.assertEqual(set(qs), {self.st1, self.st2})

    def test_filter_by_classroom(self):
        qs = StudentFilter(
            {"classroom": self.c2.classroom_id}, queryset=Student.objects.all()
        ).qs
        self.assertEqual(list(qs), [self.st2])

    def test_filter_by_firstname_and_lastname(self):
        qs_first = StudentFilter(
            {"firstname": "anan"}, queryset=Student.objects.all()
        ).qs
        self.assertEqual(set(qs_first), {self.st1, self.st3})

        qs_last = StudentFilter(
            {"lastname": "deejai"}, queryset=Student.objects.all()
        ).qs
        self.assertEqual(list(qs_last), [self.st2])

    def test_filter_by_gender(self):
        qs = StudentFilter(
            {"gender": Gender.FEMALE}, queryset=Student.objects.all()
        ).qs
        self.assertEqual(set(qs), {self.st2, self.st3})

    def test_combined_filters(self):
        qs = StudentFilter(
            {
                "school": self.s1.school_id,
                "classroom": self.c1.classroom_id,
                "firstname": "anan",
                "gender": Gender.MALE,
            },
            queryset=Student.objects.all(),
        ).qs
        self.assertEqual(list(qs), [self.st1])


class SchoolAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="school_tester", password="testpassword123"
        )
        self.client.credentials(HTTP_ACCEPT="application/json")
        self.client.force_authenticate(user=self.user)

        self.s1 = School.objects.create(
            school_fullname="Bangkok Wittaya School",
            school_shortname="BWS",
            school_add="123 Sukhumvit Rd, Bangkok",
        )
        self.s2 = School.objects.create(
            school_fullname="Chiang Mai International Academy",
            school_shortname="CMIA",
            school_add="99 Nimman Rd, Chiang Mai",
        )

    def test_unauthenticated_list_rejected(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/schools/")
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_create_school(self):
        payload = {
            "school_fullname": "Phuket Science School",
            "school_shortname": "PSS",
            "school_add": "55 Thalang Rd, Phuket",
        }
        response = self.client.post("/api/v1/schools/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["school_fullname"], "Phuket Science School")
        self.assertEqual(response.data["school_shortname"], "PSS")
        self.assertTrue(
            School.objects.filter(school_id=response.data["school_id"]).exists()
        )

    def test_list_and_filter_schools_by_name(self):
        response = self.client.get("/api/v1/schools/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        by_fullname = self.client.get("/api/v1/schools/", {"name": "wittaya"})
        self.assertEqual(by_fullname.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["school_id"] for item in by_fullname.data], [self.s1.school_id]
        )

        by_shortname = self.client.get("/api/v1/schools/", {"name": "cmi"})
        self.assertEqual(by_shortname.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["school_id"] for item in by_shortname.data], [self.s2.school_id]
        )

    def test_retrieve_school_detail_counts(self):
        c1 = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="1", school=self.s1
        )
        c2 = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="2", school=self.s1
        )
        other_c = Classroom.objects.create(
            classroom_year="M.2", classroom_tap="1", school=self.s2
        )

        # Teacher assigned to 2 classrooms of the same school should be counted once
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

        response = self.client.get(f"/api/v1/schools/{self.s1.school_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["school_id"], self.s1.school_id)
        self.assertEqual(response.data["classroom_count"], 2)
        self.assertEqual(response.data["teacher_count"], 2)
        self.assertEqual(response.data["student_count"], 2)

    def test_update_school_patch_and_put(self):
        patch_resp = self.client.patch(
            f"/api/v1/schools/{self.s1.school_id}/",
            {"school_shortname": "BWS-NEW"},
            format="json",
        )
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.s1.refresh_from_db()
        self.assertEqual(self.s1.school_shortname, "BWS-NEW")

        put_resp = self.client.put(
            f"/api/v1/schools/{self.s1.school_id}/",
            {
                "school_fullname": "Bangkok Wittaya Academy",
                "school_shortname": "BWA",
                "school_add": "456 Rama IV Rd, Bangkok",
            },
            format="json",
        )
        self.assertEqual(put_resp.status_code, status.HTTP_200_OK)
        self.s1.refresh_from_db()
        self.assertEqual(self.s1.school_fullname, "Bangkok Wittaya Academy")
        self.assertEqual(self.s1.school_shortname, "BWA")
        self.assertEqual(self.s1.school_add, "456 Rama IV Rd, Bangkok")

    def test_delete_school(self):
        response = self.client.delete(f"/api/v1/schools/{self.s1.school_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(School.objects.filter(school_id=self.s1.school_id).exists())


class ClassroomAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="classroom_tester", password="testpassword123"
        )
        self.client.credentials(HTTP_ACCEPT="application/json")
        self.client.force_authenticate(user=self.user)

        self.s1 = School.objects.create(
            school_fullname="Bangkok Wittaya School",
            school_shortname="BWS",
            school_add="123 Sukhumvit Rd",
        )
        self.s2 = School.objects.create(
            school_fullname="Chiang Mai School",
            school_shortname="CMS",
            school_add="99 Nimman Rd",
        )
        self.c1 = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="1", school=self.s1
        )
        self.c2 = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="2", school=self.s1
        )
        self.c3 = Classroom.objects.create(
            classroom_year="M.2", classroom_tap="1", school=self.s2
        )

    def test_create_classroom(self):
        payload = {
            "classroom_year": "M.3",
            "classroom_tap": "4",
            "school": self.s1.school_id,
        }
        response = self.client.post("/api/v1/classrooms/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["classroom_year"], "M.3")
        self.assertEqual(response.data["school"], self.s1.school_id)
        self.assertTrue(
            Classroom.objects.filter(
                classroom_id=response.data["classroom_id"]
            ).exists()
        )

    def test_list_and_filter_classrooms_by_school(self):
        response = self.client.get("/api/v1/classrooms/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        filtered = self.client.get(
            "/api/v1/classrooms/", {"school": self.s1.school_id}
        )
        self.assertEqual(filtered.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {item["classroom_id"] for item in filtered.data},
            {self.c1.classroom_id, self.c2.classroom_id},
        )

    def test_retrieve_classroom_detail_with_nested_teachers_and_students(self):
        teacher = Teacher.objects.create(
            teacher_firstname="Somchai",
            teacher_lastname="Jaidee",
            teacher_gender=Gender.MALE,
        )
        teacher.classrooms.add(self.c1)

        student = Student.objects.create(
            student_firstname="Anan",
            student_lastname="Sukjai",
            student_gender=Gender.MALE,
            classroom=self.c1,
        )

        response = self.client.get(f"/api/v1/classrooms/{self.c1.classroom_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["classroom_id"], self.c1.classroom_id)
        self.assertEqual(
            response.data["teachers"],
            [
                {
                    "teacher_id": teacher.teacher_id,
                    "teacher_firstname": "Somchai",
                    "teacher_lastname": "Jaidee",
                    "teacher_gender": Gender.MALE,
                }
            ],
        )
        self.assertEqual(
            response.data["students"],
            [
                {
                    "student_id": student.student_id,
                    "student_firstname": "Anan",
                    "student_lastname": "Sukjai",
                    "student_gender": Gender.MALE,
                }
            ],
        )

    def test_update_classroom_patch_and_put(self):
        patch_resp = self.client.patch(
            f"/api/v1/classrooms/{self.c1.classroom_id}/",
            {"classroom_tap": "9"},
            format="json",
        )
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.c1.refresh_from_db()
        self.assertEqual(self.c1.classroom_tap, "9")

        put_resp = self.client.put(
            f"/api/v1/classrooms/{self.c1.classroom_id}/",
            {
                "classroom_year": "M.4",
                "classroom_tap": "2",
                "school": self.s2.school_id,
            },
            format="json",
        )
        self.assertEqual(put_resp.status_code, status.HTTP_200_OK)
        self.c1.refresh_from_db()
        self.assertEqual(self.c1.classroom_year, "M.4")
        self.assertEqual(self.c1.classroom_tap, "2")
        self.assertEqual(self.c1.school_id, self.s2.school_id)

    def test_delete_classroom(self):
        response = self.client.delete(f"/api/v1/classrooms/{self.c1.classroom_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Classroom.objects.filter(classroom_id=self.c1.classroom_id).exists()
        )


class TeacherAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="teacher_tester", password="testpassword123"
        )
        self.client.credentials(HTTP_ACCEPT="application/json")
        self.client.force_authenticate(user=self.user)

        self.s1 = School.objects.create(
            school_fullname="Bangkok Wittaya School",
            school_shortname="BWS",
            school_add="123 Sukhumvit Rd",
        )
        self.s2 = School.objects.create(
            school_fullname="Chiang Mai School",
            school_shortname="CMS",
            school_add="99 Nimman Rd",
        )
        self.c1 = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="1", school=self.s1
        )
        self.c2 = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="2", school=self.s1
        )
        self.c3 = Classroom.objects.create(
            classroom_year="M.2", classroom_tap="1", school=self.s2
        )

        # Assigned to 2 classrooms in s1
        self.t1 = Teacher.objects.create(
            teacher_firstname="Somchai",
            teacher_lastname="Jaidee",
            teacher_gender=Gender.MALE,
        )
        self.t1.classrooms.add(self.c1, self.c2)

        self.t2 = Teacher.objects.create(
            teacher_firstname="Suda",
            teacher_lastname="Rakdee",
            teacher_gender=Gender.FEMALE,
        )
        self.t2.classrooms.add(self.c2)

        self.t3 = Teacher.objects.create(
            teacher_firstname="Narin",
            teacher_lastname="Jaidee",
            teacher_gender=Gender.OTHER,
        )
        self.t3.classrooms.add(self.c3)

    def test_create_teacher_with_multiple_and_no_classrooms(self):
        multi_resp = self.client.post(
            "/api/v1/teachers/",
            {
                "teacher_firstname": "Prasert",
                "teacher_lastname": "Meechai",
                "teacher_gender": Gender.MALE,
                "classrooms": [self.c1.classroom_id, self.c2.classroom_id],
            },
            format="json",
        )
        self.assertEqual(multi_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            set(multi_resp.data["classrooms"]),
            {self.c1.classroom_id, self.c2.classroom_id},
        )

        empty_resp = self.client.post(
            "/api/v1/teachers/",
            {
                "teacher_firstname": "Kanya",
                "teacher_lastname": "Srisuk",
                "teacher_gender": Gender.FEMALE,
                "classrooms": [],
            },
            format="json",
        )
        self.assertEqual(empty_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(empty_resp.data["classrooms"], [])

        omitted_resp = self.client.post(
            "/api/v1/teachers/",
            {
                "teacher_firstname": "Wichai",
                "teacher_lastname": "Panya",
                "teacher_gender": Gender.OTHER,
            },
            format="json",
        )
        self.assertEqual(omitted_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(omitted_resp.data["classrooms"], [])

    def test_list_and_filter_teachers(self):
        all_resp = self.client.get("/api/v1/teachers/")
        self.assertEqual(all_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(all_resp.data), 3)

        # Must return t1 ONCE (no duplicates) despite assignment to 2 classrooms in s1
        by_school = self.client.get("/api/v1/teachers/", {"school": self.s1.school_id})
        self.assertEqual(by_school.status_code, status.HTTP_200_OK)
        school_teacher_ids = [item["teacher_id"] for item in by_school.data]
        self.assertEqual(len(school_teacher_ids), 2)
        self.assertEqual(set(school_teacher_ids), {self.t1.teacher_id, self.t2.teacher_id})

        by_classroom = self.client.get(
            "/api/v1/teachers/", {"classroom": self.c1.classroom_id}
        )
        self.assertEqual(by_classroom.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["teacher_id"] for item in by_classroom.data], [self.t1.teacher_id]
        )

        by_firstname = self.client.get("/api/v1/teachers/", {"firstname": "som"})
        self.assertEqual(by_firstname.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["teacher_id"] for item in by_firstname.data], [self.t1.teacher_id]
        )

        by_lastname = self.client.get("/api/v1/teachers/", {"lastname": "jaidee"})
        self.assertEqual(by_lastname.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {item["teacher_id"] for item in by_lastname.data},
            {self.t1.teacher_id, self.t3.teacher_id},
        )

        by_gender = self.client.get("/api/v1/teachers/", {"gender": Gender.FEMALE})
        self.assertEqual(by_gender.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["teacher_id"] for item in by_gender.data], [self.t2.teacher_id]
        )

        combined = self.client.get(
            "/api/v1/teachers/",
            {
                "school": self.s1.school_id,
                "lastname": "jaidee",
                "gender": Gender.MALE,
            },
        )
        self.assertEqual(combined.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["teacher_id"] for item in combined.data], [self.t1.teacher_id]
        )

    def test_retrieve_teacher_detail_with_nested_classrooms(self):
        response = self.client.get(f"/api/v1/teachers/{self.t1.teacher_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["teacher_id"], self.t1.teacher_id)
        self.assertEqual(len(response.data["classrooms"]), 2)
        self.assertIsInstance(response.data["classrooms"][0], dict)
        self.assertEqual(
            {c["classroom_id"] for c in response.data["classrooms"]},
            {self.c1.classroom_id, self.c2.classroom_id},
        )
        self.assertEqual(
            set(response.data["classrooms"][0].keys()),
            {"classroom_id", "classroom_year", "classroom_tap", "school"},
        )

    def test_update_teacher_patch_and_put(self):
        patch_resp = self.client.patch(
            f"/api/v1/teachers/{self.t1.teacher_id}/",
            {"teacher_firstname": "Somchai-Updated"},
            format="json",
        )
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.t1.refresh_from_db()
        self.assertEqual(self.t1.teacher_firstname, "Somchai-Updated")

        put_resp = self.client.put(
            f"/api/v1/teachers/{self.t1.teacher_id}/",
            {
                "teacher_firstname": "Sompop",
                "teacher_lastname": "Chaiyo",
                "teacher_gender": Gender.OTHER,
                "classrooms": [self.c3.classroom_id],
            },
            format="json",
        )
        self.assertEqual(put_resp.status_code, status.HTTP_200_OK)
        self.t1.refresh_from_db()
        self.assertEqual(self.t1.teacher_firstname, "Sompop")
        self.assertEqual(self.t1.teacher_gender, Gender.OTHER)
        self.assertEqual(list(self.t1.classrooms.all()), [self.c3])

    def test_delete_teacher(self):
        response = self.client.delete(f"/api/v1/teachers/{self.t1.teacher_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Teacher.objects.filter(teacher_id=self.t1.teacher_id).exists())


class StudentAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="student_tester", password="testpassword123"
        )
        self.client.credentials(HTTP_ACCEPT="application/json")
        self.client.force_authenticate(user=self.user)

        self.s1 = School.objects.create(
            school_fullname="Bangkok Wittaya School",
            school_shortname="BWS",
            school_add="123 Sukhumvit Rd",
        )
        self.s2 = School.objects.create(
            school_fullname="Chiang Mai School",
            school_shortname="CMS",
            school_add="99 Nimman Rd",
        )
        self.c1 = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="1", school=self.s1
        )
        self.c2 = Classroom.objects.create(
            classroom_year="M.1", classroom_tap="2", school=self.s1
        )
        self.c3 = Classroom.objects.create(
            classroom_year="M.2", classroom_tap="1", school=self.s2
        )

        self.st1 = Student.objects.create(
            student_firstname="Anan",
            student_lastname="Sukjai",
            student_gender=Gender.MALE,
            classroom=self.c1,
        )
        self.st2 = Student.objects.create(
            student_firstname="Malee",
            student_lastname="Deejai",
            student_gender=Gender.FEMALE,
            classroom=self.c2,
        )
        self.st3 = Student.objects.create(
            student_firstname="Ananya",
            student_lastname="Sukjai",
            student_gender=Gender.FEMALE,
            classroom=self.c3,
        )

    def test_create_student_and_reject_missing_classroom(self):
        valid_resp = self.client.post(
            "/api/v1/students/",
            {
                "student_firstname": "Nicha",
                "student_lastname": "Wattana",
                "student_gender": Gender.FEMALE,
                "classroom": self.c1.classroom_id,
            },
            format="json",
        )
        self.assertEqual(valid_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(valid_resp.data["classroom"], self.c1.classroom_id)
        self.assertTrue(
            Student.objects.filter(student_id=valid_resp.data["student_id"]).exists()
        )

        invalid_resp = self.client.post(
            "/api/v1/students/",
            {
                "student_firstname": "Nicha",
                "student_lastname": "Wattana",
                "student_gender": Gender.FEMALE,
            },
            format="json",
        )
        self.assertEqual(invalid_resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("classroom", invalid_resp.data)

    def test_list_and_filter_students(self):
        all_resp = self.client.get("/api/v1/students/")
        self.assertEqual(all_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(all_resp.data), 3)

        by_school = self.client.get("/api/v1/students/", {"school": self.s1.school_id})
        self.assertEqual(by_school.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {item["student_id"] for item in by_school.data},
            {self.st1.student_id, self.st2.student_id},
        )

        by_classroom = self.client.get(
            "/api/v1/students/", {"classroom": self.c2.classroom_id}
        )
        self.assertEqual(by_classroom.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["student_id"] for item in by_classroom.data], [self.st2.student_id]
        )

        by_firstname = self.client.get("/api/v1/students/", {"firstname": "anan"})
        self.assertEqual(by_firstname.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {item["student_id"] for item in by_firstname.data},
            {self.st1.student_id, self.st3.student_id},
        )

        by_lastname = self.client.get("/api/v1/students/", {"lastname": "deejai"})
        self.assertEqual(by_lastname.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["student_id"] for item in by_lastname.data], [self.st2.student_id]
        )

        by_gender = self.client.get("/api/v1/students/", {"gender": Gender.FEMALE})
        self.assertEqual(by_gender.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {item["student_id"] for item in by_gender.data},
            {self.st2.student_id, self.st3.student_id},
        )

        combined = self.client.get(
            "/api/v1/students/",
            {
                "school": self.s1.school_id,
                "classroom": self.c1.classroom_id,
                "firstname": "anan",
                "gender": Gender.MALE,
            },
        )
        self.assertEqual(combined.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["student_id"] for item in combined.data], [self.st1.student_id]
        )

    def test_retrieve_student_detail_with_nested_classroom(self):
        response = self.client.get(f"/api/v1/students/{self.st1.student_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["student_id"], self.st1.student_id)
        self.assertEqual(
            response.data["classroom"],
            {
                "classroom_id": self.c1.classroom_id,
                "classroom_year": "M.1",
                "classroom_tap": "1",
                "school": self.s1.school_id,
            },
        )

    def test_update_student_patch_and_put(self):
        patch_resp = self.client.patch(
            f"/api/v1/students/{self.st1.student_id}/",
            {"student_firstname": "Anan-Updated"},
            format="json",
        )
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.st1.refresh_from_db()
        self.assertEqual(self.st1.student_firstname, "Anan-Updated")

        put_resp = self.client.put(
            f"/api/v1/students/{self.st1.student_id}/",
            {
                "student_firstname": "Arthit",
                "student_lastname": "Sawang",
                "student_gender": Gender.OTHER,
                "classroom": self.c2.classroom_id,
            },
            format="json",
        )
        self.assertEqual(put_resp.status_code, status.HTTP_200_OK)
        self.st1.refresh_from_db()
        self.assertEqual(self.st1.student_firstname, "Arthit")
        self.assertEqual(self.st1.student_gender, Gender.OTHER)
        self.assertEqual(self.st1.classroom_id, self.c2.classroom_id)

    def test_delete_student(self):
        response = self.client.delete(f"/api/v1/students/{self.st1.student_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Student.objects.filter(student_id=self.st1.student_id).exists()
        )
