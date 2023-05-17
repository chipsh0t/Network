from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from testCredentials import credDict,postsList
import time
import random

CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_experimental_option('detach',True)

class NetworkTests:
    def __init__(self):
        self.driver = webdriver.Chrome(options=CHROME_OPTIONS)

    #checks if user is logged in
    def is_logged_in(self)->bool:
        logged_in  = True
        try:
            logout_button = self.driver.find_element(by='id', value='logout-button')
        except NoSuchElementException:
            logged_in = False
        return logged_in

    def test_registration(self, username:str):
        if(not self.is_logged_in()):
            self.driver.get('http://127.0.0.1:8000/register')
            #find fields
            username_input = self.driver.find_element(by='id',value='registration-username-field') 
            email_input = self.driver.find_element(by='id',value='registration-email-field') 
            password_input = self.driver.find_element(by='id',value='registration-password-field') 
            password_conf_input = self.driver.find_element(by='id',value='registration-confirmpass-field')
            reg_submit_button = self.driver.find_element(by='id',value='registration-button')
            #send inputs
            username_input.send_keys(credDict[f'{username}_name'])
            email_input.send_keys(credDict[f'{username}_mail'])
            password_input.send_keys(credDict[f'{username}_password'])
            password_conf_input.send_keys(credDict[f'{username}_password'])
            #register
            reg_submit_button.click()


    def test_login(self, username:str):
        if(not self.is_logged_in()):
            self.driver.get('http://127.0.0.1:8000/login')
            #find fields
            username_input = self.driver.find_element(by='id',value='login-username-field') 
            password_input = self.driver.find_element(by='id',value='login-password-field') 
            login_submit_button = self.driver.find_element(by='id',value='login-button')
            #send inputs
            username_input.send_keys(credDict[f'{username}_name'])
            password_input.send_keys(credDict[f'{username}_password'])
            #login
            login_submit_button.click()

    def test_create_post(self):
        if(self.is_logged_in()):
            self.driver.get('http://127.0.0.1:8000')
            #find post form fields
            post_textarea = self.driver.find_element(by='id', value='create_post_textarea')
            post_button = self.driver.find_element(by='id', value='create_post_button')
            #send inputs
            post_content = postsList[random.randint(0,len(postsList)-1)]
            post_textarea.send_keys(post_content)
            #create post
            post_button.click()


    def test_logout(self):
        logout_button = self.driver.find_element(by='id', value='logout-button')
        logout_button.click()


def run_test(testsClass:NetworkTests, username:str, postsNum:int)->None:
    testsClass.test_registration(username)
    for _ in range(postsNum):
        testsClass.test_create_post()
    time.sleep(2)
    testsClass.test_logout()

       
def main():
    tests = NetworkTests()
    #run tests for 3 different users
    run_test(tests,'user1',11)
    run_test(tests,'user2',11)
    run_test(tests,'user3',9)
    #left on user3 to see the results
    tests.test_login('user3')
    

if __name__ == '__main__':
    main()