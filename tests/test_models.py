import warnings
warnings.filterwarnings("ignore")

from datetime import datetime, timedelta
import unittest
from config import Config
from app import create_app, db
from app.main.models import User, Student, Professor, SAPosition, Course, CourseSection, SAApplication, ApplicationStatus
from werkzeug.security import check_password_hash


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class TestModels(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_creation(self):
        u = User(username='user@wpi.edu', firstname='user', lastname='name')
        u.set_password('testpassword')
        db.session.add(u)
        db.session.commit()
        self.assertEqual(u.username, 'user@wpi.edu')
        self.assertTrue(check_password_hash(u.password_hash, 'testpassword'))

    def test_student_creation(self):
        u = Student(username='username@wpi.edu', firstname='user2', lastname='name', major='Computer Science', gpa=3.7, graduation=2025)
        u.set_password('studentpassword')
        db.session.add(u)
        db.session.commit()
        self.assertEqual(u.major, 'Computer Science')
        self.assertEqual(u.gpa, 3.7)
        self.assertEqual(u.graduation, 2025)
        self.assertTrue(check_password_hash(u.password_hash, 'studentpassword'))

    def test_professor_creation(self):
        u = Professor(username='prof@wpi.edu', firstname='prof', lastname='name', phone='123-456-7890')
        u.set_password('profpassword')
        db.session.add(u)
        db.session.commit()
        self.assertEqual(u.phone, '123-456-7890')
        self.assertTrue(check_password_hash(u.password_hash, 'profpassword'))

    def test_sa_position_creation(self):
        student = Student(username='stu@wpi.edu', firstname='stu', lastname='dent', major='Biology', gpa=3.8, graduation=2024)
        db.session.add(student)
        db.session.commit()  

        course = Course(name='CS1101-Intro to Programming')
        db.session.add(course)
        db.session.commit()  

        course_section = CourseSection(section_num='001', term='2024A', professor_id=1, course_id=course.id)
        db.session.add(course_section)
        db.session.commit()  

        sa_position = SAPosition(course_section_id=course_section.id, num_sa_required=2, min_gpa=3.5, min_grade='B')
        db.session.add(sa_position)
        db.session.commit()  

        self.assertIsNotNone(sa_position.id)  
        self.assertEqual(sa_position.course_section_id, course_section.id)
        self.assertEqual(sa_position.num_sa_required, 2)


    def test_course_creation(self):
        course = Course(name='Introduction to Python')
        db.session.add(course)
        db.session.commit()
        self.assertEqual(course.name, 'Introduction to Python')

    def test_course_section_creation(self):
        course = Course(name='Software Engineering')
        db.session.add(course)
        db.session.commit()
        section = CourseSection(section_num='001', term='2024B', professor_id=1, course_id=course.id)
        db.session.add(section)
        db.session.commit()
        self.assertEqual(section.term, '2024B')
        self.assertEqual(section.section_num, '001')


    #testapplication status and creation
    def test_sa_application_creation(self):

        student = Student(username='bob@wpi.edu', firstname='Bob', lastname='Bob', major='Physics', gpa=3.9, graduation=2023)
        db.session.add(student)
        db.session.commit()

        course = Course(name='CS 1101')
        db.session.add(course)
        db.session.commit()
        
        course_section = CourseSection(section_num='001', term='2024A', professor_id=1, course_id=course.id) 
        db.session.add(course_section)
        db.session.commit()

        sa_position = SAPosition(course_section_id=course_section.id, num_sa_required=2, min_gpa=3.5, min_grade='B')
        db.session.add(sa_position)
        db.session.commit()

        app = SAApplication(
            student_id=student.id, 
            course_section_id=course_section.id, 
            position_id=sa_position.id, 
            grade_earned='A', 
            term_taken='2024A', 
            term_applied='2024B'
        )
        db.session.add(app)
        db.session.commit()

        self.assertEqual(app.grade_earned, 'A')
        self.assertEqual(app.term_taken, '2024A')
        self.assertEqual(app.status.name, 'Pending')
        self.assertEqual(app.student_id, student.id)
        self.assertEqual(app.course_section_id, course_section.id)
        self.assertEqual(app.position_id, sa_position.id)



if __name__ == '__main__':
    unittest.main(verbosity=1)