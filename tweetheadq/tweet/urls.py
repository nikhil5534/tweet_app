from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.tweet_list , name='tweet_list'),
    path('create/', views.tweet_create , name='tweet_create'),
    path('<int:tweet_id>/edit/', views.tweet_edit, name='tweet_edit'),
    path('<int:tweet_id>/delete/', views.tweet_delete, name='tweet_delete'),
    path('register/', views.register, name='register'),
    path('user/<str:username>/', views.user_tweets, name='user_tweets'),
    path('tweet/<int:tweet_id>/like/', views.toggle_like, name='toggle_like'),
    # tweet/urls.py
    path('tweet/<int:tweet_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    # search-users
    path('search-users/', views.search_users, name='search_users'),
]
