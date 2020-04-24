from datetime import datetime
from app import db



userRoles =db.Table("userRoles",
            db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
            db.Column("role_id", db.Integer(), db.ForeignKey("role.id"))
            )
    


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quizName = db.Column(db.String(140))
    quizDescription = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    questions = db.relationship('quizQuestions', backref='quiz', cascade="all, delete-orphan")

    quizAttempt = db.relationship('quizAttempts', backref='quizAttempted', lazy='dynamic',  cascade="all, delete-orphan")


    def __repr__(self):
        return '{}'.format(self.quizName)

class quizQuestions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(140))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    quesType = db.Column(db.String(10))
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
    ansSubmit = db.Column(db.String(140))
    mark = db.Column(db.Integer)