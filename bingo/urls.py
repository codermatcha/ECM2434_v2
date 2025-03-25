from django.urls import path, re_path, include
from . import views

from .views import (
    register_user, login_user, check_auth, tasks,
    pending_tasks, complete_task, approve_task,
    leaderboard, update_user_profile, check_developer_role,
    get_user_profile, debug_user_tasks, debug_media_urls, force_award_pattern
    , reject_task, password_reset_request, password_reset_confirm,get_user_badges,index,api_test
)

# URL Patterns

from django.urls import path, re_path
from django.contrib.staticfiles.views import serve
 
urlpatterns = [
        path('api-config/', views.api_config, name='api_config'),
        path('api/test/', api_test, name='api_test'),
    path('', views.home_view, name='home'),
    path('register/', register_user, name='register_user'),
    path('login/', login_user, name='login_user'),
    path('check-auth/', check_auth, name='check_auth'),
    path('tasks/', tasks, name='tasks'),
    path('pending-tasks/', pending_tasks,name = 'pending-tasks'),
    path('complete_task/', complete_task, name='complete_task'),
    path('approve-task/', approve_task, name='approve_task'),
    path('leaderboard/', leaderboard, name='leaderboard'),
    path('profile/update/', update_user_profile, name='update_user_profile'),
    path('check-developer-role/', check_developer_role, name='check_developer_role'),
    path('profile/', get_user_profile, name='get_user_profile'),
    path('debug-tasks/', debug_user_tasks, name='debug_user_tasks'),
    path('debug-media/', debug_media_urls, name='debug_media_urls'),
    path('api/badges/', get_user_badges, name='user_badges'),
    path('force-award-pattern/', force_award_pattern, name='force_award_pattern'),
    path('reject-task/', reject_task, name='reject_task'),
    path('password-reset/', password_reset_request, name='password_reset_request'),
    path('password-reset/confirm/', password_reset_confirm, name='password_reset_confirm'),
    path('manifest.json', serve, {'path': 'manifest.json'}),
    re_path('.*', index, name='index'),
]
