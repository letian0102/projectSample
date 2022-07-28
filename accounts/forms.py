from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User
from django.utils.text import capfirst
from django.forms import ModelForm, TextInput, EmailInput
from .models import *

class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
    
    username = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'id': 'userfield'
        }
    ))

    password1 = forms.CharField(label= 'Password', widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'createpassfield',
            'name': 'Create Password'
        }
    ))

    password2 = forms.CharField(label= 'Confirm Password', widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'id': 'confirmpassfield',
            'name': 'Confirm Password'
        }
    ))

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = '__all__'
    
    title = forms.CharField(label='Title', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Title',
            'id': 'titlefield'
        }
    ))
    service = forms.CharField(label='Service', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Service',
            'id': 'servicefield'
        }
    ))
    genre = forms.CharField(required=False, label='Genres', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Genres',
            'id': 'genrefield'
        }
    ))
    runtime = forms.CharField(required=False, label='Runtime', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': '65 min',
            'id': 'runtimefield'
        }
    ))
    episodes = forms.IntegerField(required=False, label='Episodes', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': '12',
            'id': 'episodefield'
        }
    ))
    rating = forms.FloatField(required=False, label='Rating', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': '5.0',
            'id': 'ratingfield'
        }
    ))
    content_type = forms.CharField(required=False, label='Content Type', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Movie',
            'id': 'contenttypefield'
        }
    ))
    priority = models.IntegerField(default=ContentPriority.NORMAL, choices=ContentPriority.choices)

SERVICES = [
    ('netflix', 'Netflix'),
    ('prime', 'Prime Video'),
    ('funi', 'Funimation'),
]

class ImportForm(forms.ModelForm):
    class Meta:
        model = Import
        fields = '__all__'
    
    service = forms.CharField(label='Service', widget=forms.Select(
        choices=SERVICES,
        attrs={
            'class': 'form-control',
            'id': 'service'
        }
    ))
    email = forms.CharField(label='Email', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Email',
            'id': 'userfield'
        }
    ))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'createpassfield',
            'name': 'Create Password'
        }
    ))
    profile = forms.CharField(required=False, label='Profile name', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Profile name (if applicable)',
            'id': 'profilename',
            'name': 'Profile Name (if applicable)'
        }
    ))

sort_choices = [
    ("old", "Oldest First"),
    ("new", "Newest First"),
    ("highP", "Highest Priority"),
    ("lowP", "Lowest Priority"),
    ("highR", "Highest Rating"),
    ("lowR", "Lowest Rating"),
]
class SortFilterForm(forms.Form):
    
    title_name = forms.CharField(required=False, label='Title Search', widget=forms.TextInput(
        attrs={
            'placeholder': 'Show Title',
            'id': 'titlesearch',
            'name': 'Name'
        }
    ))

    service_name = forms.CharField(required=False, label='Service Search', widget=forms.TextInput(
        attrs={
            'placeholder': 'Service',
            'id': 'servicesearch',
            'name': 'Service'
        }
    ))

    genre = forms.CharField(required=False, label='Genre Search', widget=forms.TextInput(
        attrs={
            'placeholder': 'Genre(s)',
            'id': 'genresearch',
            'name': 'Genre'
        }
    ))

    sorts = forms.ChoiceField(choices=sort_choices, initial='old')

