import selenium as sel
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep

#Parameters for sign-in later. Will be mutable later, default for testing
email = 'bendude7@gmail.com'
pw = 'dummy pass'

# Set correct serivce and create website
serv = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=serv)
driver.maximize_window()

# Opens dummy crunchyroll.com
driver.get('https://www.amazon.com/Prime-Video/b?node=2676882011')

# Find button to sign in.
drop_down = driver.find_element(By.XPATH, '//a[@data-nav-role="signin"]')
drop_down.click()

# Find the email and password fields, input our values and click sign in
url = driver.current_url
email_input = driver.find_element(By.ID, 'ap_email')
email_input.send_keys(email)
cont = driver.find_element(By.ID, 'continue')
cont.click()
sleep(2)
pass_input = driver.find_element(By.ID, 'ap_password')
pass_input.send_keys(pw)
sign_in = driver.find_element(By.ID, 'signInSubmit')
sign_in.click()
WebDriverWait(driver, 20).until(EC.url_changes(url))

# Selects watchlist button, then clicks to navigate to the page.
# The wait is necessary because Amazon may think the bot is a hacker, and you will need to allow the sign-in attempt.
my_list = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.LINK_TEXT, 'My Stuff')))
my_list.click()
sleep(2)

all_content = driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/div/div/div/div[2]/div[1]/a[3]')
all_content.click()
sleep(5)

# Uses the END key to scroll the page, scrolling a lot
body = driver.find_element(By.XPATH, '//body')
prev_height = 0
while True:
    sleep(2)
    body.send_keys(Keys.END)
    curr_height = driver.execute_script('return document.body.scrollHeight')
    if curr_height == prev_height:
        break
    prev_height = curr_height

contents = driver.find_elements(By.XPATH, '/html/body/div[1]/div[4]/div/div/div/div[3]/div/div/div/div/div/div[2]/a')
titles = [link.get_attribute('aria-label') for link in contents]

for title in titles:
    print(title)
