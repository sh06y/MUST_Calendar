# login page based on selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

def login(username, password):
	# headless mode
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('--headless')
	chrome_options.add_argument('--disable-gpu')
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('--disable-dev-shm-usage')

	driver = webdriver.Chrome(options=chrome_options)
	driver.get('https://login.must.edu.mo/login')

	account = driver.find_element(By.ID, 'username')
	account_password = driver.find_element(By.ID, 'password')
	submit = driver.find_element(By.ID, 'submitButton')

	account.send_keys(username)
	account_password.send_keys(password)
	# check privacy policy
	privacy_policy = driver.find_element(By.ID, 'checkboxByPrivacyPolicy')
	privacy_policy.click()

	submit.click()

	time.sleep(3)


	return driver

	# driver.close()


	
# if __name__ == '__main__':
