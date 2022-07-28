from django.urls import path
from django.views.generic.base import TemplateView
from .views import *

urlpatterns = [
    path('login/', AuthView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('add_content/', AddView.as_view(), name='manuallyadd'),
    path('import_content/', ImportView.as_view(), name='importadd'),
    path('edit/<pk>', EditTitleView.as_view(), name='edit'),
    path('delete/<pk>', DeleteTitleView.as_view(), name='delete'),
    path('addlist/', watchlist_add, name='watchlist_add'),
    path('importlist/', import_add, name='import_add'),
    path('edit-title/', title_edit, name='title_edit')
    
]
