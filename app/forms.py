from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FieldList, FormField, RadioField, Form, SelectField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import *


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    userFullName = StringField('User Full Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    userType = SelectField("Type", choices = [("admin", "Admin"), ("user", "User"), ("overview", "Overview")])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')



class quesAndAnswer(Form):
    quesType = SelectField("Type", choices = [("shortAns", "Short Answer"), ("longAns", "Long Answer"), ("multi", "Multi-Choice"), ("fillIn", "Fill-in-the-Blank")])
    quizQuestion = StringField("Question", validators=[DataRequired()])
    quizAnswer = StringField("Answer")
    option1 = StringField("Option: ")
    option2 = StringField("Option: ")
    option3 = StringField("Option: ")
    



class quizCreation(FlaskForm):
    quizName = StringField("Quiz Name: ", validators=[DataRequired()])
    quizDescription = StringField("Quiz Description: ")
    question = FieldList(FormField(quesAndAnswer), min_entries=1)
    quizCategory = StringField("New Quiz Category: ")
    submit = SubmitField('Create')

    def validate_quizName(self, quizName):
        quiz = Quiz.query.filter_by(quizName=quizName.data).first()
        if quiz is not None:
            raise ValidationError('Quiz Name already taken')

class quizAttempt(FlaskForm):
    submit = SubmitField('Submit')

