from datetime import datetime
from app import db, admin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from flask_admin.contrib.sqla import ModelView
from flask_admin.base import MenuLink
from sqlalchemy.ext.hybrid import hybrid_property

userRoles =db.Table("userRoles",
            db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
            db.Column("role_id", db.Integer(), db.ForeignKey("role.id"))
            )
    
class quizCategory(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    
    def __repr__(self):
        return "{}".format(self.name)



quizCategories = db.Table("quizCategories",
            db.Column("quiz_id", db.Integer(), db.ForeignKey("quiz.id")),
            db.Column("quizCategory_id", db.Integer(), db.ForeignKey(quizCategory.id))
            )

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    userFullName = db.Column(db.String(140))
    email = db.Column(db.String(120), index=True, unique=True)
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



    @hybrid_property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, new_pass):
        new_password_hash = generate_password_hash(new_pass)
        self.password_hash = new_password_hash



class UserView(ModelView):
    form_columns = ["username", "userFullName", "email", "roles", "password"]
    column_list = ["username", "userFullName", "email", "roles"]



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
    quizName = db.Column(db.String(140), unique=True)
    quizDescription = db.Column(db.String(140))
    category = db.relationship('quizCategory', secondary=quizCategories, backref=db.backref('quizzes', lazy='dynamic'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    questions = db.relationship('quizQuestions', backref='quiz', cascade="all, delete-orphan")
    attempts = db.relationship('quizAttempts', backref='quizAttempted', lazy='dynamic',  cascade="all, delete-orphan")


    def __repr__(self):
        return '{}'.format(self.quizName)



class quizQuestions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(140))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    quesType = db.Column(db.String(10))
    options = db.Column(db.String(140))
    answer = db.relationship('quizAnswers', backref='question', cascade="all, delete-orphan")

    quesAttempt = db.relationship('quizAttempts', backref='quesAttempted', lazy='dynamic',  cascade="all, delete-orphan")

    def __repr__ (self):
        return '{}'.format(self.question)

class quizAnswers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quest_id = db.Column(db.Integer, db.ForeignKey('quiz_questions.id'))
    answer = db.Column(db.String(140))
    def __repr__ (self):
        return '{}'.format(self.answer)

class quizAttempts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    quest_id = db.Column(db.Integer, db.ForeignKey('quiz_questions.id'))
    quizAttemptNo = db.Column(db.Integer)
    ansSubmit = db.Column(db.String(140))
    mark = db.Column(db.Integer)
    def __repr__ (self):
        return '{}'.format(self.ansSubmit)


admin.add_view(UserView(User, db.session))
admin.add_view(ModelView(Quiz,db.session, endpoint="quizView"))
admin.add_view(ModelView(quizQuestions,db.session))
admin.add_view(ModelView(quizAnswers,db.session))
admin.add_view(ModelView(quizAttempts,db.session))

