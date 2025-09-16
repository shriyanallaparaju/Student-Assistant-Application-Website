from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, SelectField, IntegerField, FloatField, HiddenField
from wtforms.validators import  Length, DataRequired, Email, EqualTo, ValidationError, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput
from flask_login import current_user

from app import db
from app.main.models import Professor, Student, CourseSection, Course
import sqlalchemy as sqla

def get_courselabel(theCourse):
    return theCourse.name

class CourseSectionForm(FlaskForm):
    the_course = QuerySelectField('Course', 
                                   query_factory=lambda: db.session.scalars(sqla.select(Course)),  
                                   get_label= lambda theCourse : theCourse.name,
                                   allow_blank=False
                                )
    section_num = StringField('Section Number', validators=[DataRequired(), Length(max=10)])
    term = SelectField(
        'Term', 
        choices=[('A-Term', 'A-Term'), 
                 ('B-Term', 'B-Term'), 
                 ('C-Term', 'C-Term'), 
                 ('D-Term', 'D-Term')], 
        validators=[DataRequired()]
        )
    
    submit = SubmitField('Create Section')

def get_course_sections():
    return CourseSection.query.all()
def get_courseSection_name(courseSections):
    return courseSections.section_num + "-" + get_courselabel(courseSections.the_course)

class AddSAPositionForm(FlaskForm):
    the_course = QuerySelectField('Course', 
                                   query_factory=lambda: db.session.scalars(sqla.select(Course)),  
                                   get_label= lambda theCourse : theCourse.name,
                                   allow_blank=False
                                )
    num_sa_required = IntegerField(
        'Number of SAs Required', 
        validators=[DataRequired(), NumberRange(min=1, message='Must be at least one SA')]
    )
    qualifications = TextAreaField('Qualifications', validators=[Length(max=500)])
    
    min_gpa = FloatField('Minimum GPA Required', validators=[DataRequired(), NumberRange(min=0, max=4, message="GPA must be between 0 and 4.")])
    min_grade = SelectField(
        'Minimum Grade Earned in Course', 
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('NR', 'NR')],
        validators=[DataRequired()]
    )
    
    submit = SubmitField('Add Position')

class ApplicationForm(FlaskForm):
    position_id = HiddenField("Position ID", validators=[DataRequired()])
    grade_earned = StringField('Grade Earned when you Took Course:', validators=[DataRequired()])
    term_taken = StringField('Year and Term you Took Course:', validators=[DataRequired(), Length(max=100)])
    term_applied = StringField('Year and Term you are Applying For:', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Apply for SA Position')