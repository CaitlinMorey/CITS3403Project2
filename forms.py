from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField
from wtforms.validators import DataRequired

class answer(FlaskForm):
    quizQuestion = StringField("Question", validators=[DataRequired()])
    quizAnswer = StringField("Answer", validators=[DataRequired()])
    option1 = StringField("Option 1: ")
    option2 = StringField("Option 2: ")
    option3 = StringField("Option 3: ")
    #Options = RadioField('Options', choices=[('one','hyper text markup language'),
                                             #('two','home tool markup language'),
                                             #('three','hyperlinks and text markup language')])
    
class results(FlaskForm):
    #userAnswer = RadioField("Choice", choices=[form.option1.data])
    submit = SubmitField('Submit')
