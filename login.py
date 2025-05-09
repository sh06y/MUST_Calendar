# login page based on selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

class Login:
	def __init__(self, username, password):
		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument('--headless')
		chrome_options.add_argument('--disable-gpu')
		chrome_options.add_argument('--no-sandbox')
		chrome_options.add_argument('--disable-dev-shm-usage')
		self.driver = webdriver.Chrome(options=chrome_options)
		self.username = username
		self.password = password
		self._login()

	def _login(self):
		self.driver.get('https://login.must.edu.mo/login')
		account = self.driver.find_element(By.ID, 'username')
		account_password = self.driver.find_element(By.ID, 'password')
		submit = self.driver.find_element(By.ID, 'submitButton')
		account.send_keys(self.username)
		account_password.send_keys(self.password)
		privacy_policy = self.driver.find_element(By.ID, 'checkboxByPrivacyPolicy')
		privacy_policy.click()
		submit.click()
		time.sleep(3)

	def get_driver(self):
		return self.driver

	def close(self):
		self.driver.close()
