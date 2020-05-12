from datetime import datetime
from app import db, admin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import MenuLink
from sqlalchemy.ext.hybrid import hybrid_property
from flask_admin.contrib.sqla.filters import BaseSQLAFilter, FilterEqual, FilterLike, FilterInList

userRoles =db.Table("userRoles",
            db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
            db.Column("role_id", db.Integer(), db.ForeignKey("role.id"))
            )
    

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    userFullName = db.Column(db.String(128))
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    quizzes = db.relationship('Quiz', backref='author', lazy='dynamic', cascade="all, delete-orphan")

    roles = db.relationship('Role', secondary=userRoles, backref=db.backref('users', lazy='dynamic'))

    quizAttempts = db.relationship('quizAttempts', backref='user', lazy='dynamic',  cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return 'Username: {}, Name: {}'.format(self.username, self.userFullName, self.roles) #Tells python how to print objects from this class


    #For flask admin user creation
    @hybrid_property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, new_pass):
        new_password_hash = generate_password_hash(new_pass)
        self.password_hash = new_password_hash


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    
    def __repr__(self):
        return "{}".format(self.name)



class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quizName = db.Column(db.String(128), unique=True)
    quizDescription = db.Column(db.String(128))

    category_id = db.Column(db.Integer, db.ForeignKey('quiz_category.id'))
    
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    questions = db.relationship('quizQuestions', backref='quiz', cascade="all, delete-orphan")
    answers = db.relationship('quizAnswers', backref='quiz', cascade="all, delete-orphan")
    attempts = db.relationship('quizAttempts', backref='quizAttempted', lazy='dynamic',  cascade="all, delete-orphan")


    def __repr__(self):
        return '{}'.format(self.quizName)


class quizCategory(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    
    quizzes = db.relationship("Quiz", backref="category", lazy="dynamic")

    def __repr__(self):
        return "{}".format(self.name)


class quizQuestions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(128))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    quesType = db.Column(db.String(10))
    options = db.Column(db.String(128))
    answer = db.relationship('quizAnswers', backref='question', cascade="all, delete-orphan")

    quesAttempt = db.relationship('quizAttempts', backref='quesAttempted', lazy='dynamic',  cascade="all, delete-orphan")

    def __repr__ (self):
        return '{}'.format(self.question)

class quizAnswers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quest_id = db.Column(db.Integer, db.ForeignKey('quiz_questions.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    answer = db.Column(db.String(140))
    
    def __repr__ (self):
        return '{}'.format(self.answer, self.question.quiz)

class quizAttempts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    quest_id = db.Column(db.Integer, db.ForeignKey('quiz_questions.id'))
    quizAttemptNo = db.Column(db.Integer)
    ansSubmit = db.Column(db.String(128))
    feedback = db.Column(db.String(256))
    mark = db.Column(db.Integer)
    def __repr__ (self):
        return '{}'.format(self.ansSubmit)


def getUserNames():
    uniqueUserNames = User.query.filter(User.roles.any(name="user")).all()
    return [(user.username, user.username) for user in uniqueUserNames]

def getQuizNames():
    uniqueQuizNames = []
    attempts = quizAttempts.query.all()
    for at in attempts:
        entry = (at.quiz_id, at.quizAttempted)
        if entry not in uniqueQuizNames:
            uniqueQuizNames.append(entry)
        else:
            continue
    return uniqueQuizNames

def getCategoryNames():
    categories = []
    quizzes = Quiz.query.all()
    for quiz in quizzes:
        entry = (quiz.category_id, quiz.category)
        if entry not in categories:
            categories.append(entry)
        else:
            continue
    return categories

class attemptsView(ModelView):
    column_filters = [
        FilterEqual(column=User.username, name='User', options=getUserNames),
        FilterEqual(column=quizAttempts.quiz_id, name='Quiz', options=getQuizNames),
    ]
    column_labels = {"quizAttemptNo":"Attempt No.", "ansSubmit":"Answer Submitted", "quizAttempted":"Quiz", "quesAttempted":"Question"}
    can_create = False

    @expose('/')
    def index_view(self):
        self._refresh_filters_cache()
        return super(attemptsView, self).index_view()

class AnswerView(ModelView):
    can_create = False
   
class questionView(ModelView):
    can_create = False


class UserView(ModelView):
    form_columns = ["username", "userFullName", "email", "roles", "password"]
    column_labels = {"userFullName": "Full Name", "email": "Email", "roles": "Roles"}
    column_list = ["username", "userFullName", "email", "roles"]

class quizView(ModelView):
    column_filters = [
        FilterEqual(column=Quiz.category_id, name='Category', options=getCategoryNames),]
    
    column_list = ["quizName", "quizDescription", "category", "timestamp", "author"]
    column_labels = {"quizName":"Quiz Name", "quizDescription":"Quiz Description","timestamp":"Date Created","category":"Category"}

    @expose('/')
    def index_view(self):
        self._refresh_filters_cache()
        return super(quizView, self).index_view()



admin.add_view(UserView(User, db.session))
admin.add_view(quizView(Quiz,db.session, endpoint="quizView"))
admin.add_view(questionView(quizQuestions,db.session, "Questions"))
admin.add_view(AnswerView(quizAnswers,db.session, "Answers"))
admin.add_view(attemptsView(quizAttempts,db.session, "Attempts"))



