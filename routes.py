from flask import flash, request, render_template, redirect, url_for
from app import app
from app.forms import answer

@app.route('/')
@app.route('/create')
def creation():
    form = answer()
    
    return render_template('create.html', form=form)

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
    form = answer()
    name = "Caitlin"
    correct = 0
    ans = []
    
    results = request.form.to_dict()
    
    ans.append(results.values())
   
    if ans == form.quizAnswer.data:
        correct =+ 1
    else:
        correct =+ 0
    return render_template('results.html', correct = correct, form = form, name = name)





