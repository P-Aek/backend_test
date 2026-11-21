from django.contrib import admin
from django.db import IntegrityError
from django.test import TestCase

from apis.admin import ClassroomAdmin, SchoolAdmin, StudentAdmin, TeacherAdmin
from apis.models import Classroom, Gender, School, Student, Teacher


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
