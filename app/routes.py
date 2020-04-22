from flask import render_template, flash, redirect, url_for
from app import app
from flask_login import current_user, login_user
from app.models import *
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from app import db
from app.forms import *
from flask_login import logout_user
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import json


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
            next_page = url_for('dash')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/dash', methods=['GET', 'POST'])
@login_required
def dash():
    quizzes = Quiz.query.all()
    attempts = quizAttempts
    if str(current_user.roles) == "[admin]":
        return render_template("adminDash.html", quizzes=quizzes)
    elif str(current_user.roles) == "[user]":
        return render_template("userDash.html", quizzes=quizzes, quizAttempts=attempts)
    else:
        return render_template("viewDash.html", quizzes=quizzes)


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

        userRole = Role.query.filter_by(name="user").first()
        if userRole is None:
            userRole = Role(name="user")
            db.session.add(userRole)
        adminRole = Role.query.filter_by(name="admin").first()
        if adminRole is None:
            adminRole = Role(name="admin")
            db.session.add(adminRole)
        viewRole = Role.query.filter_by(name="view").first()
        if viewRole is None:
            viewRole = Role(name="view")
            db.session.add(viewRole)

        user = User(username=form.username.data,email=form.email.data, userFullName=form.userFullName.data)
        user.set_password(form.password.data)
        print(form.userType.data)
        if form.userType.data == "admin":
            adminRole.users.append(user)
        elif form.userType.data == "user":
            userRole.users.append(user)
        else:
            viewRole.users.append(user)
        
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('dash'))
    return render_template('register.html', title='Register', form=form)



@app.route("/deleteAccount/<username>")
def deleteAccount(username):
    userObj = User.query.filter_by(username=username).first()
    db.session.delete(userObj)
    db.session.commit()
    return redirect(url_for("profile"))

@app.route("/deleteQuiz/<quizName>")
def deleteQuiz(quizName):
    quizObj = Quiz.query.filter_by(quizName=quizName).first()
    db.session.delete(quizObj)
    db.session.commit()
    return redirect(url_for("dash"))


@app.route("/takeQuiz/<quizName>/", methods=['GET', 'POST'])
def takeQuiz(quizName):
    quiz = Quiz.query.filter_by(quizName=quizName).first()
    form = quizAttempt()

    #Add answer type to each question
    for ques in range(0, len(quiz.questions)):
        if quiz.questions[ques].quesType == "shortAns":
            setattr(quizAttempt, "ques"+str(ques + 1), StringField("Answer:"))    
        if quiz.questions[ques].quesType == "longAns":
            setattr(quizAttempt, "ques"+str(ques + 1), TextAreaField("Answer:",  render_kw={"rows": 20, "cols": 50}))
        if quiz.questions[ques].quesType == "multi":
############# up to mutli choice display in quiz attempts            
        
    if form.validate_on_submit():
        for ques in range(0, len(quiz.questions)):
            if str(quiz.questions[ques].answer[0]) != "":
                if str(quiz.questions[ques].answer[0]) in form.data["ques" + str(ques+1)]:
                    mark = 1
                else:
                    mark = 0    
            else:
                mark=None
            attempt = quizAttempts(user=current_user, quizAttempted=quiz, quesAttempted=quiz.questions[ques], ansSubmit=form.data["ques" + str(ques+1)], mark=mark)
            db.session.add(attempt)
            db.session.commit()
        print(form.data)
        print("submitted")
    return render_template('quizAttempt.html', quiz=quiz, form=form)

@app.route("/createQuiz", methods=['GET', 'POST'])
def createQuiz():
    form = quizCreation()
    if form.validate_on_submit():
        quiz = Quiz(quizName=form.quizName.data, quizDescription=form.quizDescription.data, author=current_user)
        
        for ques in form.question.data:
            if ques["quesType"] == "multi":
                options = [form.question.data[0]["option1"], form.question.data[0]["option2"], form.question.data[0]["option3"]]
                ques["quizQuestion"] = str({ques["quizQuestion"]:options})
            
            newQuestion = quizQuestions(question=ques["quizQuestion"], quesType=ques["quesType"], quiz=quiz)
            newAnswer = quizAnswers(answer=ques["quizAnswer"], question=newQuestion)
            db.session.commit()
        return redirect(url_for("dash"))
    return render_template("quizCreation.html", form=form)



