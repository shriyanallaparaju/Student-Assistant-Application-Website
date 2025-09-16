from app import db
import os
from typing import Optional
from flask import render_template, flash, redirect, url_for, request, session
import sqlalchemy as sqla
import identity.web
from app.main.models import Student, Professor, PastEnrollment, Course
from app.auth.auth_forms import LoginForm, MemberRegForm, StaffRegForm
from flask_login import login_user, current_user, logout_user, login_required
from app.auth import auth_blueprint as auth
from app.main.models import User, Student, Professor

from config import Config
import identity.web
import requests
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session


ssoauth= identity.web.Auth(
    session=session,
    authority=os.environ.get("AUTHORITY"),
    client_id=os.environ.get("CLIENT_ID"),
    client_credential=os.environ.get("CLIENT_SECRET"),
)


@auth.route('/student/register', methods=['GET', 'POST'])
def register_student():
    form = MemberRegForm()
    if form.validate_on_submit():
        student = Student(
            username=form.username.data,
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            major=form.major.data,
            gpa=form.gpa.data,
            graduation=form.graduation.data,
            id=form.id.data
        )
        print(form.username.data)
        print(form.firstname.data)
        print(form.lastname.data)
        print("course data:::")
        print(form.courses_saed.data)
        print(form.past_enrollments.data)

        print(student)
        student.set_password(form.password.data)
        db.session.add(student)
        # db.session.commit()

        # print(form.courses_saed.data)
        for i in range(len(form.courses_saed.data)):
            print(form.courses_saed.data[i])
            the_course = Course.query.filter_by(id=form.courses_saed.data[i].id).first()
            print(form.courses_saed.data[i].id)
            if the_course:
                student.courses_saed.add(the_course)

            else:
                new_course = Course(id = i, name = form.courses_saed.data[i].name)
                db.session.add(new_course)
                db.session.commit()

        
        
        for i in range(len(form.past_enrollments.data)):
            the_past_enrollment = PastEnrollment.query.filter_by(id=form.past_enrollments.data[i].id).first()
            if the_past_enrollment:
                student.past_enrollments.add(the_past_enrollment)
            else:
                new_past_enrollment = PastEnrollment(id = i, name = form.past_enrollments.data[i].name)
                db.session.add(new_past_enrollment)
                db.session.commit()

        print(form.courses_saed.data)

        db.session.commit()
        flash('Student registered successfully!')
        return redirect(url_for('auth.login'))
    return render_template('registerStu.html', form=form)



@auth.route('/professor/register', methods=['GET', 'POST'])
def register_professor():
    form = StaffRegForm()
    if form.validate_on_submit():
        professor = Professor(
            username=form.username.data,
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            id=form.id.data
        )
        professor.set_password(form.password.data)
        db.session.add(professor)
        db.session.commit()
        flash('Professor registered successfully!')
        return redirect(url_for('auth.login'))
    return render_template('registerProf.html', form=form)


""" Updated this to have SSO and normal login in same route!
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if isinstance(current_user, Student):
            return redirect(url_for('main.index_student'))
        if isinstance(current_user, Professor):
            return redirect(url_for('main.index_instructor'))

    form = LoginForm()
    if form.validate_on_submit():
        student = Student.query.filter_by(username=form.username.data).first()
        if student and student.get_password(form.password.data):
            login_user(student, remember=form.remember_me.data)
            flash(f"Welcome back, {student.firstname}!")
            return redirect(url_for('main.index_student'))

        professor = Professor.query.filter_by(username=form.username.data).first()
        if professor and professor.get_password(form.password.data):
            login_user(professor, remember=form.remember_me.data)
            flash(f"Welcome back, {professor.firstname}!")
            return redirect(url_for('main.index_instructor'))

        flash('Invalid username or password')
    return render_template('login.html', form=form) """




@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if isinstance(current_user, Student):
            return redirect(url_for('main.index_student'))
        if isinstance(current_user, Professor):
            return redirect(url_for('main.index_instructor'))

    # form stuff
    form = LoginForm()
    if form.validate_on_submit():
        student = Student.query.filter_by(username=form.username.data).first()
        if student and student.get_password(form.password.data):
            login_user(student, remember=form.remember_me.data)
            flash(f"Welcome back, {student.firstname}!")
            return redirect(url_for('main.index_student'))

        professor = Professor.query.filter_by(username=form.username.data).first()
        if professor and professor.get_password(form.password.data):
            login_user(professor, remember=form.remember_me.data)
            flash(f"Welcome back, {professor.firstname}!")
            return redirect(url_for('main.index_instructor'))

        flash('Invalid username or password')

    sso_url = None
    if not current_user.is_authenticated:
        sso_url = ssoauth.log_in(
            scopes=["User.Read"],
            redirect_uri=url_for("auth.auth_response", _external=True),
            prompt="select_account"
        ).get('auth_uri')  # Get the authentication URI from SSO login

    return render_template('login.html', form=form, sso_url=sso_url)





@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    # Check if the user is logged in via SSO
    if current_user.is_authenticated: 
        # Log out from both Flask and SSO
        logout_user()
        return redirect(ssoauth.log_out(url_for('auth.login', _external=True)))
    else:
        # Log out from Flask only
        logout_user()
        return redirect(url_for('auth.login'))


#route for sso
""" Added this to the normal login so they can be on the same html page
@auth.route("/sso_login")
def ssologin(): 
    return render_template("sso_login.html", **ssoauth.log_in(
        scopes=["User.Read"], 
        redirect_uri=url_for("auth.auth_response", _external=True), 
        prompt="select_account"
    ))
 """

@auth.route(Config.REDIRECT_PATH)  
def auth_response():
    result = ssoauth.complete_log_in(request.args)  

    if "error" in result:
        flash('Invalid SSO login: ' + result.get('error_description', 'Unknown error'))
        return redirect(url_for('auth.login'))  

    preferred_username = result.get('preferred_username')  # the email from preferred_username
    email = preferred_username 

    if not email:
        flash('No valid email found in the SSO response.')
        return redirect(url_for('auth.login'))  

    # Check if the user exists in the database by username 
    user = User.query.filter((User.username == preferred_username)).first() 
    print(user)

    if user is None:
        # If user does not exist, prompt to make an account!
        flash('You need to register first!')
        return redirect(url_for('auth.login'))
        
    if user:
        # Log the user in
        login_user(user)
        if isinstance(user, Student):
            return redirect(url_for('main.index_student'))  
        elif isinstance(user, Professor):
            return redirect(url_for('main.index_instructor')) 