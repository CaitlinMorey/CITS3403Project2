from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


userRoles =db.Table("userRoles",
            db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
            db.Column("role_id", db.Integer(), db.ForeignKey("role.id"))
            )

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    userFullName = db.Column(db.String(140))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    quizzes = db.relationship('Quiz', backref='author', lazy='dynamic')
    roles = db.relationship('Role', secondary=userRoles, backref=db.backref('users', lazy='dynamic'))
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {} {} {}>'.format(self.username, self.userFullName, self.roles) #Tells python how to print objects from this class


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
    quizName = db.Column(db.String(140))
    quizDescription = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    def __repr__(self):
        return 'Quiz Name: {}'.format(self.quizName)
