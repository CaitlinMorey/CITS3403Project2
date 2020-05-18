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

  def test_user_get_id(self):
    mark=User()
    mark.username='username1'
    mark.email='username@student.com'
    db.session.add(mark)
    db.session.commit()
    assert_that(type(mark.get_id())).is_equal_to(type(1))

  def test_user_validate(self):
    validUser=User()
    invalidUser=User()
    validUser.username='username'
    validUser.userFullName = 'userFullName'
    validUser.email='emailaddress@student.com'
    assert_that(validUser.validate()).is_equal_to(True)
    assert_that(invalidUser.validate()).is_equal_to(False)

    invalidUser.username=None
    invalidUser.userFullName='userFullName'
    invalidUser.email='emailaddress@student.com'
    assert_that(invalidUser.validate()).is_equal_to(False)

    invalidUser.username='username'
    invalidUser.userFullName=None
    invalidUser.email='emailaddress@student.com'
    assert_that(invalidUser.validate()).is_equal_to(False)

    invalidUser.username='username'
    invalidUser.userFullName='userFullName'
    invalidUser.email=None
    assert_that(invalidUser.validate()).is_equal_to(False)
  
  def test_getUserById(self):
    inputId = 1
    assert_that(User.getUserById(inputId).id).is_equal_to(inputId)
  
  def test_getUserByUserName(self):
    inputName = 'mark'
    assert_that(User.getUserByUserName(inputName).username).is_equal_to(inputName)

  def test_numberOfUsers(self):
    self.assertEqual(len(User.getAllUsers()), len(User.query.all())) 
    
if __name__ == '__main__':
  unittest.main(verbosity=2)