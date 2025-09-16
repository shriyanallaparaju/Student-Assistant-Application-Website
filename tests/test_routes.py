import os
from config import Config
import sqlalchemy as sqla
import pytest
from app import create_app, db
from app.main.models import User, Student, Professor, Course, PastEnrollment, SAApplication, SAPosition, CourseSection, ApplicationStatus, studentCourses, studentPastEnrollments


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SECRET_KEY = 'bad-bad-key'
    WTF_CSRF_ENABLED = False
    DEBUG = True
    TESTING = True

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app(config_class=TestConfig)
    testing_client = flask_app.test_client()
    ctx = flask_app.app_context()
    ctx.push()
    yield testing_client
    ctx.pop()

@pytest.fixture
def init_database():

    db.create_all()
    yield
    db.session.remove()
    db.drop_all()

def register_student(test_client, username, password):
    return test_client.post('/student/register', 
                            data=dict(
                                username=username,
                                password=password,
                                firstname='Test',
                                lastname='Student',
                                major='Computer Science',
                                gpa='3.5',
                                graduation='2023',
                                id='123',
                                courses_saed=['CS 1004 - Introduction To Programming For Non-Majors'],
                                past_enrollments=['CS 1004 - Introduction To Programming For Non-Majors']

                            ), 
                            follow_redirects=True)

def register_professor(test_client, username, password):
    return test_client.post('/professor/register', 
                            data=dict(
                                username=username,
                                password=password,
                                password2=password,  
                                firstname='Test',
                                lastname='Professor',
                                id='456',
                                number='555-555-5555'  
                            ), 
                            follow_redirects=True)


def login_user(test_client, path, username, password):
    response = test_client.post(path, 
                            data=dict(username=username, password=password, remember_me=False), 
                            follow_redirects=True)

    assert response.status_code == 200

def logout_user(test_client):
    return test_client.get('/logout', follow_redirects=True)

def test_register_student_page(test_client, init_database):
    response = test_client.get('/student/register')
    assert response.status_code == 200
    assert b"Register" in response.data


def test_register_student(test_client, init_database):
    
    new_course1 = Course(name = "CS3733 - Software Engineering")
    new_course2 = Course(name = "CS2223 - Algorithms")
    new_course3 = Course(name = "CS2102 - Object-Oriented Programming")

    db.session.add(new_course1)
    db.session.add(new_course2)
    db.session.add(new_course3)

    db.session.commit()

    past_enrollment1 = PastEnrollment(name = new_course1.name, course_id = new_course1.id)
    past_enrollment2 = PastEnrollment(name = new_course2.name, course_id = new_course2.id)
    past_enrollment3 = PastEnrollment(name = new_course3.name, course_id = new_course3.id)

    db.session.add(past_enrollment1)
    db.session.add(past_enrollment2)
    db.session.add(past_enrollment3)

    db.session.commit()

    # i need to find out how to put lists into the route, then this should work
    
    response = test_client.post('/student/register',
                                data=dict(username = 'stu@wpi.edu',
                                          firstname = 'Stu',
                                          lastname = 'Dent',
                                          number = '7811112222',
                                          id = 11111111,
                                          password = 'pass',
                                          password2 = 'pass',
                                          gpa = 4.0,
                                          graduation = 2027,
                                          courses_saed = [past_enrollment1.id, 2],
                                          past_enrollments = [1, 2, 3],
                                          major = 'CS'),
                                follow_redirects = True)
    
    s = db.session.scalars(sqla.select(Student).where(Student.username == 'stu@wpi.edu')).first()
    s_count = db.session.scalar(sqla.select(db.func.count()).where(User.username == 'stu@wpi.edu'))
    print(s)

    courses_as_sa = db.session.scalars(s.courses_saed.select()).all()
    courses_taken = db.session.scalars(s.past_enrollments.select()).all()

    print(courses_as_sa)
    
    assert response.status_code == 200
    
    assert s.username == 'stu@wpi.edu'
    assert s_count == 1

    assert courses_as_sa[0].name == "CS3733 - Software Engineering"
    assert courses_as_sa[1].name == "CS2223 - Algorithms"

    assert courses_taken[0].name == "CS3733 - Software Engineering"
    assert courses_taken[1].name == "CS2223 - Algorithms"
    assert courses_taken[2].name == "CS2102 - Object-Oriented Programming"

    assert b"Sign In" in response.data   
    assert b"Welcome!" in response.data
    assert b"Don't Have an Account?" in response.data


#passes yay!
def test_register_professor_page(test_client):
    response = test_client.get('/professor/register')
    assert response.status_code == 200
    assert b"Register" in response.data

def test_register_professor(test_client, init_database):

    response = test_client.post('/professor/register',
                                data=dict(username = 'prof@wpi.edu', firstname = 'Prof',
                                          lastname = 'Essor', number = '1234567890', id = 1234567890,
                                          password = 'test_pass', password2 = 'test_pass'),
                                follow_redirects = True)
    
    p = db.session.scalars(sqla.select(Professor).where(User.username == 'prof@wpi.edu')).first()
    p_count = db.session.scalar(sqla.select(db.func.count()).where(User.username == 'prof@wpi.edu'))
    
    assert response.status_code == 200
    
    assert p.username == 'prof@wpi.edu'
    assert p_count == 1
    assert b"Sign In" in response.data   
    assert b"Welcome!" in response.data
    assert b"Don't Have an Account?" in response.data

def test_index_student_get(request,test_client, init_database):
    response = test_client.get('/index_student')

    assert response.status_code == 200
    assert b"Current Courses:" in response.data

def test_login_logout(test_client, init_database):
    
    
    response = test_client.post('/logout', follow_redirects = True)
    
    assert response.status_code == 200
    assert b"Welcome back" in response.data

# def test_invalid_login(test_client, init_database):
#     response = login_user(test_client, 'nonexistent_user', 'wrongpassword')
#     assert response.status_code == 200
#     assert b"Invalid username or password" in response.data