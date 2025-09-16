from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, NumberRange, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from app.main.models import User, Student, Professor, PastEnrollment, CourseSection, Course
from flask_login import current_user
from wtforms.widgets import ListWidget, CheckboxInput
from app.main.forms import get_course_sections
from app import db
import sqlalchemy as sqla


def get_courselabel(theCourse):
    return theCourse.name

def get_pastenrollment_label(thePastEnrollment):
    return thePastEnrollment.name

#Base class for login (used for both Member and Staff login)
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=1, max=100)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me', default=False)
    submit = SubmitField('Sign In')

    def validate_username(self, username):
        student = Student.query.filter_by(username=username.data).first()
        professor = Professor.query.filter_by(username=username.data).first()
        if student is None and professor is None:
            raise ValidationError('No account with that username.')
    
#Registration form for students (members)
class MemberRegForm(FlaskForm):
    username = StringField('Username (WPI Email)', validators=[DataRequired(), Email()])
    firstname = StringField('First Name', validators=[DataRequired(), Length(min=1, max=50)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=50)])

    number = StringField('Phone Number', validators=[DataRequired()])
    major = StringField('Major', validators=[DataRequired(), Length(max=100)])
    gpa = DecimalField('GPA', places=2, validators=[Optional(), NumberRange(min=0.0, max=4.0)])
    graduation = IntegerField('Graduation Year', validators=[DataRequired(), NumberRange(min=2000, max=9999)])
    id = StringField('WPI ID', validators=[DataRequired(), Length(min=1, max=20)])
    courses_saed = QuerySelectMultipleField('Previous SA Courses',
                                            query_factory= lambda: db.session.scalars(sqla.select(Course)),
                                            get_label= lambda theCourse : theCourse.name,
                                            widget = ListWidget(prefix_label=False), 
                                            option_widget=CheckboxInput())
    
    past_enrollments = QuerySelectMultipleField('Past Enrollments',
                                                query_factory= lambda: db.session.scalars(sqla.select(PastEnrollment)),
                                                get_label = lambda thePastEnrollment : thePastEnrollment.name,
                                                widget = ListWidget(prefix_label=False),
                                                option_widget = CheckboxInput())

    password = PasswordField('Password', validators=[DataRequired(), Length(min=1)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')



    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_id(self, id):
        user = User.query.filter_by(id=id.data).first()
        if user:
            raise ValidationError('ID Already exists.')




#registration form for professors (Staff)
class StaffRegForm(FlaskForm):
    username = StringField('Username (WPI Email)', validators=[DataRequired(), Email()])
    firstname = StringField('First Name', validators=[DataRequired(), Length(min=1, max=50)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=50)])

    number = StringField('Phone Number', validators=[DataRequired()])
    id = StringField('WPI ID', validators=[DataRequired(), Length(min=1, max=20)])

    password = PasswordField('Password', validators=[DataRequired(), Length(min=1)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_id(self, id):
        user = User.query.filter_by(id=id.data).first()
        if user:
            raise ValidationError('ID Already exists.')

