from django import template
from django.contrib.messages.api import success
from django.db.models import query
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, request
from django.contrib.auth.views import LoginView
from django.urls.base import reverse
from django.views import generic
from django.shortcuts import get_object_or_404, render
from django.contrib.sessions.models import Session
from django.views.generic.edit import DeleteView, UpdateView
import selenium as sel
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import django_rq
import requests
from .forms import *
from .models import *

def get_list(request):
    if request.user.is_authenticated:
        user = request.user
        form = SortFilterForm(request.POST)
        title = None
        service = None
        genre = None
        sort = None
        if form.is_valid():
            if form.cleaned_data['title_name']:
                title = form.cleaned_data['title_name']
            if form.cleaned_data['service_name']:
                service = form.cleaned_data['service_name']
            if form.cleaned_data['genre']:
                genre = form.cleaned_data['genre']
            sort = form.cleaned_data['sorts']
        queryset, created = Watchlist.objects.get_or_create(user=user)
        

        if title and service:
            titles = queryset.shows.all().filter(title=title, service=service)
        elif title:
            titles = queryset.shows.all().filter(title=title)
        elif service:
            titles = queryset.shows.all().filter(service=service)
        else:
            titles = queryset.shows.all()
        
        if sort:
            if sort == 'new':
                titles = reversed(titles)
            elif sort == 'highP':
                titles = titles.order_by('-priority')
            elif sort == 'lowP':
                titles = titles.order_by('priority')
            elif sort == 'highR':
                titles = titles.order_by('-rating')
            elif sort == 'lowR':
                titles = titles.order_by('rating')

        context = {'title_list': titles, 'user': user, 'form': SortFilterForm}
        if genre:
            context['genre'] = genre
        return render(request, 'home.html', context)
    else:
        return render(request, 'home.html', {'form': SortFilterForm})
def import_add(request):
    if request.method == "POST":
        form = ImportForm(request.POST)
        if form.is_valid():
            messages.add_message(request, messages.WARNING, 'Importing from the service, please wait a few minutes before checking your list.')
            django_rq.get_queue('default', autocommit=True, is_async=False)
            django_rq.enqueue(import_to_list, request.user, form.cleaned_data['service'], form.cleaned_data['email'], form.cleaned_data['password'], form.cleaned_data['profile'])
    else:
        messages.add_message(request, messages.WARNING,'Form contents are invalid')
    return render(request, 'importadd.html', {'form': ImportForm})

def watchlist_add(request):
    if request.method == "POST":
        form = ContentForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            if(form.cleaned_data['genre'] == '' and form.cleaned_data['rating'] == None):
                if(form.cleaned_data['service'] == 'Funimation' or form.cleaned_data['service'] == 'Crunchyroll'):
                    obj = create_anime_content(form.cleaned_data['title'], form.cleaned_data['service'], form.cleaned_data['priority'])
                else:
                    obj = create_content(form.cleaned_data['title'], form.cleaned_data['service'], form.cleaned_data['priority'])
            else:
                obj = Content()
                obj.title = form.cleaned_data['title']
                obj.service = form.cleaned_data['service']
                if form.cleaned_data['genre']:
                    obj.genre = form.cleaned_data['genre']
                if form.cleaned_data['runtime']:
                    obj.runtime = form.cleaned_data['runtime']
                if form.cleaned_data['episodes']:
                    obj.episodes = form.cleaned_data['episodes']
                if form.cleaned_data['rating']:
                    obj.rating = form.cleaned_data['rating']
                if form.cleaned_data['content_type']:
                    obj.content_type = form.cleaned_data['content_type']
                obj.save()
                obj.priority = form.cleaned_data['priority']
            return add_to_list(request, obj)
    messages.add_message(request, messages.WARNING, 'Form contents are invalid')
    return render(request, 'manuallyadd.html', {'form': ContentForm})
    
def title_edit(request):
    if request.method == "POST":
        form = ContentForm(request.POST)
        if form.is_valid():
            obj = Content.objects.get(title=form.cleaned_data['title'], service=form.cleaned_data['service'])
            if form.cleaned_data['genre']:
                obj.genre = form.cleaned_data['genre']
            if form.cleaned_data['runtime']:
                obj.runtime = form.cleaned_data['runtime']
            if form.cleaned_data['episodes']:
                obj.episodes = form.cleaned_data['episodes']
            if form.cleaned_data['rating']:
                obj.rating = form.cleaned_data['rating']
            if form.cleaned_data['content_type']:
                obj.content_type = form.cleaned_data['content_type']
        
            obj.priority = form.cleaned_data['priority']
            obj.save()
            return get_list(request)
        else:
            messages.add_message(request, messages.WARNING, 'Edited contents are invalid')
            return render(request, 'edit.html', {'form': ContentForm})
    messages.add_message(request, messages.WARNING,'Invalid request, try again')
    return render(request, 'edit.html', {'form': ContentForm})
        
def import_to_list(user, service, email, password, profile):
    if(service == 'netflix'):
        netflix_import(user, email, password, profile)
    elif(service == 'prime'):
        prime_import(user, email, password)
    elif(service == 'funi'):
        funi_import(user, email, password)

def add_to_list(request, content):
    title_to_save = get_object_or_404(Content, pk=content.id)
    user_list, created = Watchlist.objects.get_or_create(user=request.user)
    
    if user_list.shows.all().filter(title=title_to_save.title).exists():
        messages.add_message(request, messages.ERROR, 'This title is already in your watchlist')
    else :
        user_list.shows.add(title_to_save)
        messages.add_message(request, messages.SUCCESS, "Successfully added to the watchlist")
    return render(request, 'manuallyadd.html', {'form': ContentForm})

def create_content(title, service, priority):
    sleep(2)
    obj, created = Content.objects.get_or_create(title=title, service=service)
    obj.priority = priority
    print('got or created')
    if(created):
        print('created')
        url = "https://ott-details.p.rapidapi.com/search"
        searchstring = title
        querystring = {"title": searchstring, "page": "1"}
        headers = {
            'x-rapidapi-host': "ott-details.p.rapidapi.com",
            'x-rapidapi-key': "44b752ab0bmsh5c28cdc1cb9d261p1570cejsnc07827fa91f9"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
        result = response.json()['results']
        print('queried the endpoint')
        found = False
        for res in result:
            if res['title'] == searchstring:
                show = res
                found = True
                print('found the show')
                break
        sleep(2)
        if found:
            genrestr = ''
            for genre in show['genre']:
                genrestr += genre
                genrestr += ', '
            obj.genre = genrestr
            if show['type'] == 'tvMovie' or show['type'] == 'movie':
                obj.content_type = 'Movie'
            else:
                obj.content_type = 'TV'
            print('creating another request')
            url = "https://ott-details.p.rapidapi.com/gettitleDetails"
            querystring = {"imdbid": show['imdbid']}
            response = requests.request(
                "GET", url, headers=headers, params=querystring)
            result = response.json()
            print('got request')
            if(not(show['type'] == 'tvSeries')):
                obj.runtime = result['runtime']
            if result['imdbrating']:
                obj.rating = result['imdbrating']
        print('saving')
        obj.save()
        print('saved')
    return obj

def create_anime_content(title, service, priority):
    obj, created = Content.objects.get_or_create(title=title, service=service)
    obj.priority = priority
    if(created):
        url = "https://jikan1.p.rapidapi.com/search/anime"
        searchstring = title
        querystring = {"q": searchstring}
        headers = {
            'x-rapidapi-host': "jikan1.p.rapidapi.com",
            'x-rapidapi-key': "44b752ab0bmsh5c28cdc1cb9d261p1570cejsnc07827fa91f9"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)

        result = response.json()['results']
        found = False
        for res in result:
            if res['title'] == searchstring:
                anime_show = res
                found = True
                break
        obj.genre = 'Anime, Animation, '
        obj.content_type = 'TV'
        if found:
            obj.episodes = anime_show['episodes']
            obj.rating = anime_show['score']
        elif result:
            obj.episodes = result[0]['episodes']
            obj.rating = result[0]['score']
        obj.save()
    return obj

def netflix_import(rquser, email, pw, my_name):
    try:
        options = webdriver.ChromeOptions()
        options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--mute-audio")
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)
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
        sleep(10)
        if EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[1]/div[1]/div[2]/div/div/ul/li')):
            profiles = driver.find_elements(
                By.XPATH, '/html/body/div[1]/div/div/div[1]/div[1]/div[2]/div/div/ul/li')
            print("getting profile")
            for profile in profiles:
                name = profile.find_element(By.XPATH, './/div/a/span').text
                if name == my_name:
                    profile_link = profile.find_element(By.XPATH, './/div/a')
                    profile_link.click()
                    break
            print("got profile")
        else:
            print("skipping profile")

        # Clicks "My List" link to get convenient view of user list
        sleep(5)
        print('navigating to my list page')
        driver.get('https://www.netflix.com/browse/my-list')
        print("made it to my list")
        sleep(5)
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

        for title in titles:
            print("making content")
            create_content(title, 'Netflix', 1)
            print("saved content")
            title_to_save = get_object_or_404(Content, title=title)
            user_list, created = Watchlist.objects.get_or_create(user=rquser)
            if user_list.shows.all().filter(title=title_to_save.title).exists():
                print("was already in list")
                continue
            else:
                print("added successfully")
                user_list.shows.add(title_to_save)
        
        print("all done")
    except Exception as e:
        print(e)

def prime_import(rquser, email, pw):
    try:
        # Set correct serivce and create website
        options = webdriver.ChromeOptions()
        options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--mute-audio")
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)

        # Opens dummy Prime Video
        driver.get('https://www.amazon.com/Prime-Video/b?node=2676882011')
        print("got website")
        # Find button to sign in.
        drop_down = driver.find_element(By.XPATH, '//a[@data-nav-role="signin"]')
        drop_down.click()

        # Find the email and password fields, input our values and click sign in
        url = driver.current_url
        email_input = WebDriverWait(driver,100).until(EC.presence_of_element_located((By.ID, 'ap_email')))
        email_input.send_keys(email)
        cont = driver.find_element(By.ID, 'continue')
        cont.click()
        pass_input = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.ID, 'ap_password')))
        pass_input.send_keys(pw)
        sign_in = driver.find_element(By.ID, 'signInSubmit')
        sign_in.click()
        WebDriverWait(driver, 200).until(EC.url_changes(url))

        # Selects watchlist button, then clicks to navigate to the page.
        # The wait is necessary because Amazon may think the bot is a hacker, and you will need to allow the sign-in attempt.
        my_list = WebDriverWait(driver, 500).until(EC.presence_of_element_located((By.LINK_TEXT, 'My Stuff')))
        my_list.click()

        all_content = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[4]/div/div/div/div[2]/div[1]/a[3]')))
        all_content.click()

        # Uses the END key to scroll the page, scrolling a lot
        body = driver.find_element(By.XPATH, '//body')
        prev_height = 0
        while True:
            sleep(2)
            body.send_keys(Keys.END)
            curr_height = driver.execute_script(
                'return document.body.scrollHeight')
            if curr_height == prev_height:
                break
            prev_height = curr_height

        contents = driver.find_elements(By.XPATH, '/html/body/div[1]/div[4]/div/div/div/div[3]/div/div/div/div/div/div[2]/a')
        titles = [link.get_attribute('aria-label') for link in contents]

        for title in titles:
            create_content(title, 'Prime Video', 1)
            title_to_save = get_object_or_404(Content, title=title)
            user_list, created = Watchlist.objects.get_or_create(
                user=rquser)
            if user_list.shows.all().filter(title=title_to_save.title).exists():
                continue
            else:
                user_list.shows.add(title_to_save)
    except Exception as e:
        print(e)

def funi_import(rquser, email, pw):
    try:
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
        email_input = WebDriverWait(driver, 50).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/main/div/div/div/div[2]/section[1]/div/div/div[2]/div/div/form/div[1]/input')))
        pass_input = driver.find_element(
            By.XPATH, '/html/body/main/div/div/div/div[2]/section[1]/div/div/div[2]/div/div/form/div[2]/input')
        email_input.send_keys(email)
        pass_input.send_keys(pw)
        sign_in = driver.find_element(
            By.XPATH, '/html/body/main/div/div/div/div[2]/section[1]/div/div/div[2]/div/div/form/button')
        sign_in.click()
        WebDriverWait(driver, 20).until(EC.url_changes(url))

        # Selects watchlist button, then clicks to navigate to the page.
        queue = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Queue')))
        queue.click()

        # Gets first set of titles, which dynamically load as page scrolls.
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/main/div/div/div[2]/div/div[3]/div/div[1]/ul/li[1]')))

        # Uses the END key to scroll the page, scrolling to bottom.
        sleep(5)
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

        elems = driver.find_elements(
            By.XPATH, '/html/body/main/div/div/div[2]/div/div[3]/div/div[1]/ul/li')
        titles = [el.get_attribute('data-title') for el in elems]

        for title in titles:
            obj = create_anime_content(title, 'Funimation')
            title_to_save = get_object_or_404(Content, pk=obj.pk)
            user_list, created = Watchlist.objects.get_or_create(user=rquser)
            if user_list.shows.all().filter(title=title_to_save.title).exists():
                continue
            else:
                user_list.shows.add(title_to_save)
    except Exception as e:
        print(e)

class AuthView(LoginView):
    success_url = reverse_lazy('home')
    template_name = 'registration/login.html'

class SignUpView(generic.CreateView):
    form_class = RegisterForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

class HomeView(generic.CreateView):
    form_class = SortFilterForm
    success_url = reverse_lazy('get_list')
    template_name = 'home.html'

class AddView(generic.CreateView):
    form_class = ContentForm
    template_name = 'manuallyadd.html'

class ImportView(generic.CreateView):
    form_class = ImportForm
    template_name = 'importadd.html'

class EditTitleView(UpdateView):
    model = Content
    form_class = ContentForm
    template_name = 'edit.html'
    success_url = reverse_lazy('get_list')

class DeleteTitleView(DeleteView):
    model = Content
    template_name = 'delete.html'
    success_url = reverse_lazy('get_list')
