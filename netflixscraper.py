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
from PIL import Image
from Screenshot import Screenshot_Clipping

#Parameters for sign-in later. Will be mutable later, default for testing
email = 'a_lopez@alumni.rice.edu'
pw = 'dummy pass'
# Profile needs to be EXACTLY as it is in Netflix
my_name = 'Ben'

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
options.add_argument('--ignore-certificate-errors')
options.add_argument("--mute-audio")
serv = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=serv, options=options)
driver.maximize_window()

# Opens dummy netflix.com, attempts login and waits until url changes
driver.get('https://www.netflix.com')
print("got website")
url = driver.current_url
print("finding login")
login = driver.find_element(By.CLASS_NAME, "authLinks")
print("about to click login")
login.click()
print("clicked login")
WebDriverWait(driver, 500).until(EC.url_changes(url))

# Find the email and password fields, input our values and click sign in
url = driver.current_url
print("finding email and pass")
email_input = WebDriverWait(driver, 500).until(
    EC.presence_of_element_located((By.NAME, 'userLoginId')))
pass_input = driver.find_element(By.NAME, 'password')
print("sending keys to email and pass")
email_input.send_keys(email)
pass_input.send_keys(pw)
print("finding sign in")
sign_in = driver.find_element(By.CLASS_NAME, 'login-button')
print("clicking sign in")
sign_in.click()
print("clicked, now waiting")

# Selects the correct profile, and clicks on the right one. Sleeps while waiting for load time (url does not change)
print("looking for profile")
WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[1]/div[1]/div[2]/div/div/ul/li')))
profiles = driver.find_elements(By.XPATH, '/html/body/div[1]/div/div/div[1]/div[1]/div[2]/div/div/ul/li')
driver.save_screenshot('ss1.png')
img = Image.open('ss1.png')
img.show()
if len(profiles) > 0:
    for profile in profiles:
        name = profile.find_element(By.XPATH, './/div/a/span').text
        if name == my_name:
            profile_link = profile.find_element(By.XPATH, './/div/a')
            profile_link.click()
            break
print("got profile/skipped profile")
sleep(3)
driver.save_screenshot('ss1.png')
img = Image.open('ss1.png')
# Clicks "My List" link to get convenient view of user list
url = driver.current_url
my_list = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.LINK_TEXT, 'My List')))
my_list.click()
print("made it to my list")

# Uses the END key to scroll the page, infinite scrolling (maybe change to for loop to avoid errors?)
print("scrolling")
WebDriverWait(driver, 150).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'title-card')))
body = driver.find_element(By.XPATH, '//body')
prev_height = 0
while True:
    body.send_keys(Keys.END)
    sleep(5)
    curr_height = driver.execute_script(
        'return document.body.scrollHeight')
    if curr_height == prev_height:
        break
    prev_height = curr_height
    print("scrolled")

# Wacky list comprehension gets the title text from aria-label attribute (only part in Netflix list that shows plain text)
print("getting content")
content_div = driver.find_elements(By.CLASS_NAME, 'title-card')
titles = [div.find_element(By.CSS_SELECTOR, 'a').get_attribute(
    'aria-label') for div in content_div]
print("got titles")

print(titles)
