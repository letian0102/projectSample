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
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.add_argument("--mute-audio")
serv = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=serv, options=options)
driver.maximize_window()

# Opens dummy crunchyroll.com
driver.get('https://www.funimation.com/log-in/')

# Find the email and password fields, input our values and click sign in
url = driver.current_url
email_input = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, '/html/body/main/div/div/div/div[2]/section[1]/div/div/div[2]/div/div/form/div[1]/input')))
pass_input = driver.find_element(By.XPATH, '/html/body/main/div/div/div/div[2]/section[1]/div/div/div[2]/div/div/form/div[2]/input')
email_input.send_keys(email)
pass_input.send_keys(pw)
sign_in = driver.find_element(By.XPATH, '/html/body/main/div/div/div/div[2]/section[1]/div/div/div[2]/div/div/form/button')
sign_in.click()
WebDriverWait(driver, 20).until(EC.url_changes(url))

# Selects watchlist button, then clicks to navigate to the page.
queue = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.LINK_TEXT, 'Queue')))
queue.click()

print(driver.find_element(By.XPATH, '//body').get_attribute('innerHTML'))
# Gets first set of titles, which dynamically load as page scrolls.
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/main/div/div/div[2]/div/div[3]/div/div[1]/ul/li[1]')))

# Uses the END key to scroll the page, scrolling to bottom.
body = driver.find_element(By.XPATH, '//body')
prev_height = 0
while True:
    body.send_keys(Keys.END)
    curr_height = driver.execute_script('return document.body.scrollHeight')
    if curr_height == prev_height:
        break
    prev_height = curr_height
    sleep(5)
    # Get titles currently on display in page. If they are not currently in titles, add them.

elems = driver.find_elements(By.XPATH, '/html/body/main/div/div/div[2]/div/div[3]/div/div[1]/ul/li')
titles = [el.get_attribute('data-title') for el in elems]

for title in titles:
    print(title)
