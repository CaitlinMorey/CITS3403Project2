from flask import render_template, flash, redirect, url_for
from app import app
from flask_login import current_user, login_user
from app.models import *
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm, classCreation, LoginForm, joinClass
from flask_login import logout_user


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html", title="Welcome")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/dash', methods=['GET', 'POST'])
@login_required
def dash():
    createClassForm = classCreation()

    #Creates class from submit
    if createClassForm.validate_on_submit() and createClassForm.submit1.data:
        classObj = Class.query.filter_by(
            name=createClassForm.className.data).first()
        if classObj is None:
            current_user.classes.append(
                Class(name=createClassForm.className.data))
            flash("Class created")
            db.session.commit()
        else:
            flash("Class name already Exists")
        return redirect(url_for("dash"))

    #Join user to class from form submit
    joinClassForm = joinClass()
    if joinClassForm.validate_on_submit() and joinClassForm.submit2.data:
        classObj = Class.query.filter_by(name=joinClassForm.className.data).first()
        if classObj is None:
            flash("Class does not exist!")
        else:
            classObj.members.append(current_user)
            db.session.commit()
            flash("You have joined " + classObj.name)
            return redirect(url_for("dash"))
    if str(current_user.roles) == "[teacher]":
        return render_template("teacherDash.html", createClassForm=createClassForm, joinClassForm=joinClassForm)
    else:
        return render_template("studDash.html", joinClassForm=joinClassForm)


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        studRole = Role.query.filter_by(name="student").first()
        if studRole is None:
            studRole = Role(name="student")
            db.session.add(studRole)
        teachRole = Role.query.filter_by(name="teacher").first()
        if teachRole is None:
            teachRole = Role(name="teacher")
            db.session.add(teachRole)


        if form.teacher.data == True:
            user = User(username=form.username.data,
                        email=form.email.data, userFullName=form.userFullName.data)
            user.set_password(form.password.data)
            teachRole.users.append(user)
        else:
            user = User(username=form.username.data,
                        email=form.email.data, userFullName=form.userFullName.data)
            user.set_password(form.password.data)
            studRole.users.append(user)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('dash'))
    return render_template('register.html', title='Register', form=form)


@app.route("/leaveClass/<lClass>")
def leaveClass(lClass):
    keepClasses = []
    for c in current_user.classes:
        if str(c) == lClass:
            continue
        else:
            keepClasses.append(c)
    current_user.classes = keepClasses
    db.session.commit()
    return redirect(url_for("dash"))


@app.route("/deleteClass/<rmClass>")
def deleteClass(rmClass):
    classObj = Class.query.filter_by(name=rmClass).first()
    db.session.delete(classObj)
    db.session.commit()
    return redirect(url_for("dash"))

@app.route("/deleteAccount/<username>")
def deleteAccount(username):
    userObj = User.query.filter_by(username=username).first()
    db.session.delete(userObj)
    db.session.commit()
    return redirect(url_for("profile"))