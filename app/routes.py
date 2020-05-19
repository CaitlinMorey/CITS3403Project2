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
import random
import html


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
    existingCategories = quizCategory.query.all()
    if str(current_user.roles) == "[admin]":
        return redirect("admin")
    elif str(current_user.roles) == "[user]":
        return render_template("userDash.html", quizzes=quizzes, quizAttempts=quizAttempts, quizQuestions=quizQuestions, existingCategories=existingCategories)
    else:
        return render_template("viewDash.html", quizzes=quizzes, quizAttempts=quizAttempts, quizQuestions=quizQuestions, existingCategories=existingCategories)


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dash'))
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
@login_required
def takeQuiz(quizName):
    quiz = Quiz.query.filter_by(quizName=quizName).first()
    

    #Dynamically build answer form for each question type
    for ques in range(0, len(quiz.questions)):
        if quiz.questions[ques].quesType == "shortAns":
            setattr(quizAttempt, "ques"+str(ques + 1), StringField("Answer:", [DataRequired()]))    
        if quiz.questions[ques].quesType == "longAns":
            setattr(quizAttempt, "ques"+str(ques + 1), TextAreaField("Answer:", [DataRequired()], render_kw={"rows": 20, "cols": 50}))
        if quiz.questions[ques].quesType == "multi":
            optionsStr = str(quiz.questions[ques].options).replace("'","")
            ans = str(quiz.questions[ques].answer[0])
            optionsList = optionsStr.strip('][').split(',')
            choices=[]
            for elem in range(0, len(optionsList)):
                if optionsList[elem].strip() != "":
                    choice = (optionsList[elem], html.escape(optionsList[elem]))
                    choices.append(choice)
            choices.append((ans,html.escape(ans)))
            random.shuffle(choices)
            setattr(quizAttempt, "ques"+str(ques + 1), RadioField("", [DataRequired()], choices=choices))
        if quiz.questions[ques].quesType == "fillIn":
            for i in range(0, quiz.questions[ques].question.count("*blank*")):
                setattr(quizAttempt, "ques"+str(ques + 1)+"b"+str(i), StringField("", [DataRequired()])) 

    form = quizAttempt()
    if form.validate_on_submit():
        attemptNo = 1
        
        #check if quiz has been attempted or assign attempt no.
        noOfAttempts = quizAttempts.query.filter_by(user=current_user).filter_by(quizAttempted=quiz).count() / quizQuestions.query.filter_by(quiz=quiz).count()
        if noOfAttempts != 0:
            attemptNo = noOfAttempts + 1
        #Mark each question 
        for ques in range(0, len(quiz.questions)):
            #if question answer is not "None" thus a long answer question then we check if submitted answer is in answer
            if str(quiz.questions[ques].answer[0]) != "None":
                
                if quiz.questions[ques].quesType == "fillIn":
                    #build answer string
                    ans = []
                    for i in range(0, quiz.questions[ques].question.count("*blank*")):
                        ans.append(form.data["ques" + str(ques+1) + "b" + str(i)])
                    if str(ans).strip("][").replace("'", "") == str(quiz.questions[ques].answer[0]):
                        mark = 1
                    else: 
                        mark = 0
                    ansSubmitted = str(ans).strip("][")
                else:
                    ansSubmitted = form.data["ques" + str(ques+1)]
                    if str(quiz.questions[ques].answer[0]) in ansSubmitted:
                        mark = 1
                    else:
                        mark = 0
                
            else:
                mark=None
            #Build attempt entry in quizAttempts
            attempt = quizAttempts(user=current_user, quizAttempted=quiz, quesAttempted=quiz.questions[ques], quizAttemptNo=attemptNo, ansSubmit=ansSubmitted, mark=mark, feedback=None)
            db.session.add(attempt)
            db.session.commit()
        return redirect(url_for("viewAttempt", quizAttemptView=quiz))

    return render_template('quizAttempt.html', quiz=quiz, form=form)

@app.route("/createQuiz", methods=['GET', 'POST'])
@login_required
def createQuiz():
    
    #get list of existing categories
    existingCategories = quizCategory.query.all()
    
    #add select field to quizCreation form with existing categories
    if existingCategories != []:
        #create choices field
        choices = []
        for category in existingCategories:
            choices.append((str(category),str(category)))
        setattr(quizCreation, "selectedCategory", SelectField("Category: ", choices=choices, coerce=str))

    form = quizCreation()
    if form.validate_on_submit():
        
        #Create Quiz Category if new one is specified
        if form.quizCategory.data != "":
            dbCategory = quizCategory.query.filter_by(name=form.quizCategory.data).first()
            if dbCategory is None:
                dbCategory = quizCategory(name=form.quizCategory.data)
                db.session.add(dbCategory)
        #else if quiz category is selected.
        else:
            dbCategory = quizCategory.query.filter_by(name=form.selectedCategory.data).first()

        quiz = Quiz(quizName=form.quizName.data, quizDescription=form.quizDescription.data, author=current_user, category=dbCategory)
        
        for ques in form.question.data:

            #add options to quizQuestions table from form
            options = []
            if ques["quesType"] == "multi":
                listOfOptions = ["option1", "option2", "option3"]
                for optNo in listOfOptions:
                    if ques[optNo] != "" and ques[optNo] != " ":
                        options.append(ques[optNo])           

            #ensure long answer questions have no answer attached
            if ques["quesType"] == "longAns":
                answer = None
            else:
                answer = ques["quizAnswer"]

            newQuestion = quizQuestions(question=ques["quizQuestion"], quesType=ques["quesType"], quiz=quiz)
            if options != []:
                print(options)
                newOptions = quesOptions(options=str(options), question=newQuestion)
            newAnswer = quizAnswers(answer=answer, question=newQuestion,  quiz=quiz)
        db.session.commit()
        return redirect(url_for("quizView.index_view"))
    else:
        print(form.errors)
    return render_template("quizCreation.html", form=form)


@app.route("/viewAttempt/<quizAttemptView>", methods=['GET', 'POST'])
@login_required
def viewAttempt(quizAttemptView):

    quiz = Quiz.query.filter_by(quizName=quizAttemptView).first()

    attempts = quizAttempts.query.filter_by(user=current_user).filter_by(quizAttempted=quiz).all()
    attemptsList = []
    for attempt in attempts:
        if attempt.quizAttemptNo not in attemptsList:
            attemptsList.append(attempt.quizAttemptNo)
        else:
            continue
    
    marksList = [0]*len(attemptsList)
    for attemptNo in attemptsList:
        for attempt in attempts:
            if attempt.quizAttemptNo == attemptNo:
                marksList[attemptNo-1] += attempt.mark
            else:
                continue
    noQuizQuestions = len(quiz.questions)
    
    return render_template("viewAttempt.html", attempts=attempts, quiz=quiz, attemptsList=attemptsList, quizAttempts=quizAttempts, marksList=marksList, noQuizQuestions=noQuizQuestions)

@app.route("/viewQuiz/<quizViewName>")
@login_required
def viewQuiz(quizViewName):
    quiz = Quiz.query.filter_by(quizName=quizViewName).first()
    return render_template("viewQuiz.html", quiz=quiz)

@app.route("/viewAllAttempts/<quizAllAttemptView>")
@login_required
def viewAllAttempts(quizAllAttemptView):
    quiz = Quiz.query.filter_by(quizName=quizAllAttemptView).first()
    attempts = quizAttempts.query.filter_by(quizAttempted=quiz).all()
    userList = {}
    maxAttempts = 0
    for attempt in attempts:
        if attempt.user not in userList:
            user = User.query.filter_by(username=str(attempt.user)).first()
            noUserAttempts = int(quizAttempts.query.filter_by(quizAttempted=quiz).filter_by(user=user).count() / len(quiz.questions))
            userList[attempt.user] = noUserAttempts
            if noUserAttempts > maxAttempts:
                maxAttempts = noUserAttempts
        else:
            continue
    userList["maxAttempts"] = maxAttempts
    print(userList)
    return render_template("viewAllAttempts.html", attempts=attempts, quiz=quiz, userList=userList, maxAttempts=maxAttempts)
    