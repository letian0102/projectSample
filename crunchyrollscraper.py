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
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--mute-audio")
serv = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=serv, options=options)
driver.maximize_window()

# Opens dummy crunchyroll.com
driver.get('https://www.crunchyroll.com/login')

# Find the email and password fields, input our values and click sign in
url = driver.current_url
email_input = driver.find_element(By.ID, 'login_form_name')
pass_input = driver.find_element(By.ID, 'login_form_password')
email_input.send_keys(email)
pass_input.send_keys(pw)
if len(driver.find_elements(By.CLASS_NAME, 'opt-in__close')) > 0:
    driver.find_element(By.CLASS_NAME, 'opt-in__close').click()
sign_in = driver.find_element(By.ID, 'login_submit_button')
sign_in.click()
WebDriverWait(driver, 20).until(EC.url_changes(url))

# Selects watchlist button, then clicks to navigate to the page.
sleep(1.5)
icon = driver.find_element(By.CLASS_NAME, 'erc-watchlist-header-button')
icon.click()

# Gets first set of titles, which dynamically load as page scrolls.
sleep(10)
elems = driver.find_elements(By.CLASS_NAME, 'c-watchlist-card-title__text')
titles = [elem.text for elem in elems]

# Uses the END key to scroll the page, scrolling to bottom.
body = driver.find_element(By.XPATH, '//body')
prev_height = 0
while True:
    body.send_keys(Keys.END)
    curr_height = driver.execute_script('return document.body.scrollHeight')
    if curr_height == prev_height:
        break
    prev_height = curr_height
    sleep(9)
    # Get titles currently on display in page. If they are not currently in titles, add them.
    elems = driver.find_elements(By.CLASS_NAME, 'c-watchlist-card-title__text')
    temp = [elem.text for elem in elems]
    for t in temp:
        if t not in titles:
            titles.append(t)

for title in titles:
    print(title)
