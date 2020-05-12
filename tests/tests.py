import os, unittest
from unittest import TestCase, TestSuite

from config import basedir
from app.models import *
from assertpy import assert_that

from app import app, db

class userModelCase(TestCase):
  def setUp(self):
    self.app = app
    self.app.config['TESTING'] = True
    self.app.config['WTF_CSRF_ENABLED'] = False
    self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
    self.app_context=self.app.app_context()
    self.app_context.push()
    db.create_all()

    mark=User()
    mark.username='mark'
    mark.email='mark@student.com'

    luke=User()
    luke.username='luke'
    luke.email='luke@student.com'

    db.session.add(mark)
    db.session.add(luke)
    db.session.commit()

  def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()

if __name__ == '__main__':
  unittest.main(verbosity=2)