from django.conf import settings
from django.conf.urls.static import static

from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    # Main page
    path('', views.index, name='index'),
    # Any another page
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    # User proflie
    path('profile/<str:username>/', views.profile, name='profile'),
    # Posts view
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    # Create post
    path('create/', views.post_create, name='post_create'),
    # Post edit
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment')
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
