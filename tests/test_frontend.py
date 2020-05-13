import requests, os
import unittest
from urllib.request import urlopen
from time import sleep
from flask_testing import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support import ui
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

from config import basedir
from app import app, db 
from app.models import *

class TestBase(LiveServerTestCase):  
  def create_app(self):
    self.app = app  
    return app
  def setUp(self):
    """Setup the test driver and create test users"""
    self.app = app
    self.app.config['TESTING'] = True
    self.app.config['WTF_CSRF_ENABLED'] = False
    self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
    # self.app_context=self.app.app_context()
    # self.app_context.push()
    db.create_all()

    # REQUIRED 'chromedriver 80.0.3987.106'
    chromedriver_path = os.path.abspath("chromedriver")
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
    self.driver.get(self.get_server_url())
  
    db.session.commit()
    db.drop_all()
    db.create_all()
  
  def tearDown(self):
    self.driver.quit()

  def test_server_is_up_and_running(self):
    response = urlopen(self.get_server_url())
    self.assertEqual(response.code, 200)

if __name__ == "__main__":
    unittest.main()