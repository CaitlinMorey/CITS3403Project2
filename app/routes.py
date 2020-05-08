from flask import flash, request, render_template, redirect, url_for
from app import app
from app import db
from app.models import *
from app.forms import *
from flask import jsonify

@app.route('/')
@app.route('/create', methods=['GET', 'POST'])
def creation():
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

        quiz = Quiz(quizName=form.quizName.data, quizDescription=form.quizDescription.data, author=current_user)
        dbCategory.quizzes.append(quiz) #potentially need to change if existing category is selected.
        
        for ques in form.question.data:

            #add options to quizQuestions table from form
            options = []
            listOfOptions = ["option1", "option2", "option3"]
            if ques["quesType"] == "multi":
                for optNo in listOfOptions:
                    if ques[optNo] != "" or ques[optNo] != " ":
                        options.append(ques[optNo])
            options = str(options)

            #ensure long answer questions have no answer attached
            if ques["quesType"] == "longAns":
                answer = None
            else:
                answer = ques["quizAnswer"]

            newQuestion = quizQuestions(question=ques["quizQuestion"], options=options, quesType=ques["quesType"], quiz=quiz)
            newAnswer = quizAnswers(answer=answer, question=newQuestion,  quiz=quiz)
        db.session.commit()
        return redirect(url_for("quizView.index_view"))
    else:
        print(form.errors)
    
    return render_template('create.html', form=form)

@app.route('/data')
def data():
    
    name, noAttempts = attempts()

    return render_template('data.html', noAttempts = noAttempts, name = name)

def attempts():
    
    names = quizCategory.query.all()
    name = []
    for i in names:
        name.append(str(i))
     
    noAttempts = [] #list of number of attempts for each category
    
    for n in name:
        quiz = Quiz.query.filter(Quiz.category.any(name=n)).all() #all the quizzes under that category
        
        marks = 0
        
        for i in quiz:
            Attempts = quizAttempts.query.filter_by(quizAttempted=i).all() #the attempts for each quiz
            for j in Attempts:
                if j.mark != None:
                    marks += j.mark
    
            noAttempts.append[marks]
            
    return name, noAttempts

@app.route('/json')
def getdata():
    
    values = [5,8,15]
    labels = ["CSS","HTML","Javascript"]
    
    return flask.jsonify({'payload':json.dumps({'values':values, 'labels':labels})})
    

@app.route('/stats')
def stats():
    labels = ["html", "CSS", "Javascript"]
    values = [5,10,15]
   
    return render_template('chart.html', labels = labels, values = values)


@app.route('/htmlquiz', methods=['GET', 'POST'])
def htmlquiz():
    form = answer()
    
    return render_template('questions.html', form = form)


@app.route('/login')
def login():
    name = "Caitlin"
    return render_template('login.html', name = name)


@app.route('/results', methods=['GET','POST'])
def results():
    form = quizAttempt()
    
    return render_template('results.html', correct = correct, form = form, name = name)
    


