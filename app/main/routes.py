
from app import db
from datetime import datetime
from flask import render_template, flash, redirect, url_for
import sqlalchemy as sqla

from app.main import main_blueprint as bp_routes
from app.main.models import Student, Professor, User, CourseSection, SAApplication, ApplicationStatus
from app.auth.auth_forms import MemberRegForm, StaffRegForm, LoginForm
from app.main.forms import CourseSectionForm, AddSAPositionForm, ApplicationForm
from flask_login import login_user, current_user, logout_user, login_required
from app.auth import auth_blueprint as auth
from app.main.models import SAPosition, CourseSection

@bp_routes.route('/', methods=['GET', 'POST'])

@bp_routes.route('/index_student', methods=['GET', 'POST'])
@login_required
def index_student():
    # if student is redirected to professor page
    if not isinstance (current_user, Student):
        flash("Access denied: You are not a student.")
        return redirect(url_for('main.index_instructor'))
    
    sa_positions = SAPosition.query.join(CourseSection).all()
    return render_template('index_student.html', posts=sa_positions)

@bp_routes.route('/index_instructor', methods=['GET', 'POST'])
@login_required
def index_instructor():
    # if professor is redirected to student page
    if not isinstance (current_user, Professor):
        flash("Access denied: You are not a Professor.")
        return redirect(url_for('main.index_student'))
    
    course_section_form = CourseSectionForm()
    sa_position_form = AddSAPositionForm()
    if course_section_form.validate_on_submit():
        pass
    if sa_position_form.validate_on_submit():
        pass

    # querying SA positions for the professor's courses
    sa_positions = SAPosition.query.join(CourseSection).filter(CourseSection.professor_id == current_user.id).all()

    # sa_positions = SAPosition.query.join(CourseSection).all()
    return render_template('index_instructor.html', CourseSectionForm=course_section_form, AddSAPositionForm=sa_position_form, posts=sa_positions)


@bp_routes.route('/create_course', methods=['GET', 'POST'])
@login_required
def create_course():
    # if professor is redirected to student page
    if not isinstance (current_user, Professor):
        flash("Access denied: You are not a Professor.")
        return redirect(url_for('main.index_student'))
    form = CourseSectionForm()
    if form.validate_on_submit():
        new_section = CourseSection(
            the_course=form.the_course.data,
            section_num=form.section_num.data,
            term=form.term.data,
            professor_id=current_user.id
        )
        db.session.add(new_section)
        db.session.commit()
        flash(f"{form.the_course.data} - {form.section_num.data}  ({form.term.data}) has been added!", "success")
        return redirect(url_for('main.index_instructor'))
    
    return render_template('create_course.html', form=form)

@bp_routes.route('/add_position', methods=['GET', 'POST'])
@login_required
def add_position():
    # if professor is redirected to student page
    if not isinstance (current_user, Professor):
        flash("Access denied: You are not a Professor.")
        return redirect(url_for('main.index_student'))
    sa_position_form = AddSAPositionForm()
    if sa_position_form.validate_on_submit():

        the_course = sa_position_form.the_course.data
        
        course_section = CourseSection.query.filter_by(course_id=the_course.id).first()  
        if course_section:

            sa_position = SAPosition(
                course_section_id=course_section.id, 
                num_sa_required=sa_position_form.num_sa_required.data,
                qualifications=sa_position_form.qualifications.data,
                min_gpa=sa_position_form.min_gpa.data,
                min_grade=sa_position_form.min_grade.data,
                timestamp=datetime.utcnow()
            )

            db.session.add(sa_position)
            db.session.commit()  
            flash('SA position created successfully!', 'success')
        else:
            flash('Course section not found', 'danger')
        return redirect(url_for('main.index_instructor'))
    
    return render_template('add_position.html', sa_position_form=sa_position_form)



@bp_routes.route('/applied_to_positions', methods=['GET', 'POST'])
@login_required
def sa_applyto_list():
        # if student is redirected to professor page
    if not isinstance (current_user, Student):
        flash("Access denied: You are not a student.")
        return redirect(url_for('main.index_instructor'))

    applications = SAApplication.query.filter_by(student_id=current_user.id).all()
    form = ApplicationForm()

    return render_template('applied_to_positions.html', applications=applications, form=form)

@bp_routes.route('/apply/<int:position_id>', methods=['GET', 'POST'])
@login_required
def apply_to_sa_position(position_id):
    # if student is redirected to professor page
    if not isinstance (current_user, Student):
        flash("Access denied: You are not a student.")
        return redirect(url_for('main.index_instructor'))

    the_sa_position = SAPosition.query.get(position_id)

    existing_application = SAApplication.query.filter_by(
        student_id = current_user.id, 
        position_id = position_id
        ).first()
    
    if existing_application: 
        flash("You have already applied for this position.", "info") 
        return redirect(url_for('main.index_student'))
    
    course_section_id = the_sa_position.course_section_id
    form = ApplicationForm()
    form.position_id.data = position_id
    
    if form.validate_on_submit():
        app = SAApplication(
            student_id=current_user.id,
            position_id=position_id,
            course_section_id=course_section_id,
            grade_earned=form.grade_earned.data,
            term_taken=form.term_taken.data,
            term_applied=form.term_applied.data
        )
        db.session.add(app)
        db.session.commit()
        flash("Your application has been submitted successfully! Yay!", "success")
        return redirect(url_for('main.index_student'))
    
    return render_template('apply.html', form=form, position=the_sa_position)


@bp_routes.route('/view_applied/<int:position_id>', methods=['GET'])
@login_required
def view_applied(position_id):
    # if professor is redirected to student page
    if not isinstance (current_user, Professor):
        flash("Access denied: You are not a Professor.")
        return redirect(url_for('main.index_student'))
    position = SAPosition.query.get(position_id)

    if position is None:
        flash('Position not found.', 'danger')
        return redirect(url_for('main.index_instructor'))
    
    applicants = SAApplication.query.filter_by(position_id=position.id).all()
    
    if not applicants:
        flash('No applicants for this position yet.', 'info')

    return render_template('view_applied.html', position=position, applicants=applicants)


@bp_routes.route('/hire_application/<int:application_id>', methods=['POST'])
@login_required
def hire_application(application_id):
    # is the current user a professor?
    if not isinstance(current_user, Professor):
        flash("Access denied: You are not a Professor.")
        return redirect(url_for('main.index_student'))
    
    # get the application
    application = SAApplication.query.get(application_id)

    #if the application doesn't exist, redirect
    if application is None:
        flash("Application not found.", "danger")
        return redirect(url_for('main.index_instructor'))
    
    # Check if the position is already full and then redirect
    position = application.app_position
    if position.num_sas >= position.num_sa_required:
        flash("This position is already full.", "danger")
        return redirect(url_for('main.view_applied', position_id=position.id))

    # Update the status to hired
    application.status.name = "Assigned"
    position.update_num_sas()
    db.session.commit()
    

    #student = application.student #puts none in student for some reason i think?

    #position.students.add(student) #line that doesn't work because it says the student is nonetype
    #db.session.commit()
    #flash(f"Successfully hired {student.firstname} {student.lastname} for the position!", "success")
    return redirect(url_for('main.view_applied', position_id=position.id))


@bp_routes.route('/decline_application/<int:application_id>', methods=['POST'])
@login_required
def decline_application(application_id):
    # Check if the current user is a professor
    if not isinstance(current_user, Professor):
        flash("Access denied: You are not a Professor.")
        return redirect(url_for('main.index_student'))
    
    # get app
    application = SAApplication.query.get(application_id)

    # ff the application doesn't exist, redirect
    if application is None:
        flash("Application not found.", "danger")
        return redirect(url_for('main.index_instructor'))
    
    # update status to Declined
    application.status.name = "Declined"
    
    db.session.commit()
    flash(f"Successfully declined {application.student.firstname} {application.student.lastname}'s application.", "info")
    return redirect(url_for('main.view_applied', position_id=application.app_position.id))

@bp_routes.route('/withdraw/<int:application_id>', methods=['POST'])
@login_required
def withdraw_application(application_id):
    # Find the application in the database 
    application = SAApplication.query.get(application_id)

    # if the application doesn't exist, redirect
    if not application:
        flash('Application not found', 'error')
        return redirect(url_for('main.sa_applyto_list'))
    
    # check if the application has already been assigned
    if application.status.name == "Assigned":
        flash("You cannot withdraw your application because you have been assigned to the position.", "danger")
        return redirect(url_for('main.sa_applyto_list'))
    
    if application.status.name == "Pending":
        if application.status:
            db.session.delete(application.status)

        db.session.delete(application)
            
        try:
            db.session.commit()
            flash("Application withdrawn successfully.", "success")
        except sqla.exc.IntegrityError as e:
            db.session.rollback()
            flash("Error withdrawing application: " + str(e), "danger")

    return redirect(url_for('main.sa_applyto_list'))    
