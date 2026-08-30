from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.insecure_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('search/', views.note_search, name='note_search'),
    path('account/<str:username>/', views.account_detail, name='account_detail'),
    path('comments/', views.comments, name='comments'),
    path('crash/', views.crash, name='crash'),
]
