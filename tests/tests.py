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

  def test_user_set_password(self):
    mark=User()
    mark.username='mark'
    mark.email='mark@student.com'
    mark.set_password('1234')
    assert_that(type(mark.password_hash)).is_equal_to(type('abc'))
  
  def test_user_check_password(self):
    mark=User()
    mark.username='mark'
    mark.email='mark@student.com'
    mark.set_password('1234')
    assert_that(mark.check_password('1234')).is_equal_to(True)

  
if __name__ == '__main__':
  unittest.main(verbosity=2)