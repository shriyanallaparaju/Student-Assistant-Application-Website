from datetime import datetime, timezone
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from app import db, login
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo

@login.user_loader
def load_user(id):
  return db.session.get(User, int(id))

saCourses = db.Table (
  'saCourses',
  db.metadata,
  sqla.Column('course_id', sqla.Integer, sqla.ForeignKey('course_section.id'), primary_key=True),
  sqla.Column('sa_id', sqla.Integer, sqla.ForeignKey('sa_position.id'), primary_key=True)
)

studentCourses = db.Table (
  'studentCourses',
  db.metadata,
  sqla.Column('student_id', sqla.Integer, sqla.ForeignKey('student.id'), primary_key = True),
  sqla.Column('course_id', sqla.Integer, sqla.ForeignKey('course.id'), primary_key = True)
)

studentPastEnrollments = db.Table(
    'studentPastEnrollments',
    db.metadata,
    sqla.Column('student_id', sqla.Integer, sqla.ForeignKey('student.id'), primary_key=True),
    sqla.Column('past_enrollment_id', sqla.Integer, sqla.ForeignKey('past_enrollment.id'), primary_key=True)
)


class User(db.Model, UserMixin):
  __tablename__='user'
  id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
  username : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(150), index = True, unique = True, nullable=False)
  password_hash : sqlo.Mapped[Optional[str]] = sqlo.mapped_column(sqla.String(256))
  firstname : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(120))
  lastname : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(120))
  user_type : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(50))
  __mapper_args__ = {
      'polymorphic_identity': 'User',
      'polymorphic_on':user_type
  }
  def set_password(self,password):
      self.password_hash=generate_password_hash(password)
  def get_password(self, password):
      return check_password_hash(self.password_hash, password)  

class Student(User):
    __tablename__ = 'student'
    id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(User.id), primary_key=True)
    major: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(100))
    gpa: sqlo.Mapped[Optional[float]] = sqlo.mapped_column(sqla.Float)
    graduation: sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer)

    # relationships
    applications: Mapped[list['SAApplication']] = sqlo.relationship(back_populates='student')
    
    courses_saed: sqlo.WriteOnlyMapped['Course'] = sqlo.relationship(
        secondary=studentCourses,
        #primaryjoin = (studentCourses.c.course_id == id),
        back_populates='the_students'
    )
    position : sqlo.Mapped['SAPosition'] = sqlo.relationship(back_populates = 'students')

    past_enrollments : sqlo.WriteOnlyMapped['PastEnrollment'] = sqlo.relationship(
        secondary=studentPastEnrollments,
        #primaryjoin = (studentPastEnrollments.c.past_enrollment_id == id),
        back_populates='past_students'
    )

    __mapper_args__ = {
        'polymorphic_identity': 'Student'
    }


class Professor(User):
  __tablename__ = 'professor'
  id : sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(User.id), primary_key=True)
  phone: sqlo.Mapped[Optional[str]] = sqlo.mapped_column(sqla.String(15))
  
  # relationships
  courses : Mapped[list['CourseSection']] = sqlo.relationship(back_populates = 'professor')
  
  __mapper_args__ = {
      'polymorphic_identity': 'Professor'
  }

class SAPosition(db.Model):
  __tablename__ = 'sa_position'
  id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
  course_section_id : sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('course_section.id'))
  num_sa_required : sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer)
  qualifications : sqlo.Mapped[Optional[str]] = sqlo.mapped_column(sqla.String(500))
  min_gpa = sqla.Column(sqla.Float, nullable=False)
  min_grade = sqla.Column(sqla.String(1), nullable=False)
  timestamp : sqlo.Mapped[Optional[datetime]] = sqlo.mapped_column(default = lambda : datetime.now(timezone.utc))
  num_sas: sqlo.Mapped[int] = sqlo.mapped_column(sqla.Integer, default = 0, nullable = False)

  # foreign keys
  student_id: sqlo.Mapped[Optional[int]] = sqlo.mapped_column(sqla.ForeignKey('student.id'))
  
  # relationships
  course_section = sqlo.relationship('CourseSection', backref='sa_positions', lazy=True)
  students: Mapped[list['Student']] = sqlo.relationship(back_populates='position')

  def __repr__(self):
       return f'<SAPosition {self.id} - {self.num_sa_required} SAs for {self.course_section_id}>'

  courses_as_sa : sqlo.WriteOnlyMapped['CourseSection'] = sqlo.relationship(
      secondary = saCourses,
      primaryjoin = (saCourses.c.course_id == id),
      back_populates = 'assistants')
  
  # relationship between position and the applications made for that position
  position_applications : Mapped[list['SAApplication']] = sqlo.relationship(back_populates = 'app_position')

  # helper functions

  # updates num_sas
  def update_num_sas(self):
    self.num_sas += 1

class Course(db.Model):
    __tablename__ = 'course'
    id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    name : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(100))

    # relationships
    sections : Mapped[list['CourseSection']] = sqlo.relationship(back_populates='the_course')

    the_students : sqlo.WriteOnlyMapped['Student'] = sqlo.relationship(
        secondary=studentCourses,
        #primaryjoin = (studentCourses.c.student_id == id),
        back_populates='courses_saed'
    )

    def __repr__(self):
        return f"{self.name}"
    past_enroll : sqlo.Mapped['PastEnrollment'] = sqlo.relationship(back_populates='past_course')


class CourseSection(db.Model):
  __tablename__ = 'course_section'
  id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)

  section_num : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(10))
  term : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(20))
  
  professor_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('professor.id'))
  course_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('course.id'))
  
  # relationships
  assistants : sqlo.WriteOnlyMapped['SAPosition'] = sqlo.relationship(
      secondary = saCourses,
      primaryjoin = (saCourses.c.sa_id == id),
      back_populates = 'courses_as_sa')
  
  professor : sqlo.Mapped['Professor'] = sqlo.relationship(back_populates = 'courses')

  the_course : sqlo.Mapped['Course'] = sqlo.relationship(back_populates = 'sections')
  section_applications : Mapped[list['SAApplication']] = sqlo.relationship(back_populates = 'app_course_section')


class SAApplication(db.Model):
  __tablename__ = 'sa_app'
  id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
  grade_earned : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(1))
  term_taken : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(5))
  term_applied : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(5))

  # foreign keys
  student_id : sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('student.id'))
  course_section_id : sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('course_section.id'))
  position_id : sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('sa_position.id'))

  # relationships
  student : sqlo.Mapped['Student'] = sqlo.relationship(back_populates = 'applications')
  app_course_section : sqlo.Mapped['CourseSection'] = sqlo.relationship(back_populates = 'section_applications')
  app_position : sqlo.Mapped['SAPosition'] = sqlo.relationship(back_populates = 'position_applications')
  status: sqlo.Mapped['ApplicationStatus'] = sqlo.relationship(back_populates='sa_application')

  def __init__(self, **kwargs):
     super().__init__(**kwargs)
     if self.status is None:
        self.status = ApplicationStatus(name="Pending")

class PastEnrollment(db.Model):
    __tablename__ = 'past_enrollment'
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    name : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(100))
    course_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('course.id'))

    # relationships:
    past_course: sqlo.Mapped['Course'] = sqlo.relationship(back_populates='past_enroll')
    
    past_students: sqlo.WriteOnlyMapped['Student'] = sqlo.relationship(
        secondary=studentPastEnrollments,
        #primaryjoin = (studentPastEnrollments.c.student_id == id),
        back_populates='past_enrollments'
    )

    def __repr__(self):
        return f"{self.past_course.name}"
    
class ApplicationStatus(db.Model):
  __tablename__ = 'application_status'
  id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
  name : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(100))
  application_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey('sa_app.id'))

  sa_application : sqlo.Mapped['SAApplication'] = sqlo.relationship(back_populates='status')