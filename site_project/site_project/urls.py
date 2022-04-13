"""site_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from joggerlogger import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',  views.index, name="index_page"),
    path('login/', views.login_page, name="login_page"),
    path('register/', views.register_page, name="register_page"),
    re_path('api/runs', views.api_runs, name="api_runs"),
    path('run-logging/<int:run_id>', views.run_logging, name="run_logging"),
    path('team-hall/', views.team_hall, name="team_hall"),
    path('team-detail/<int:team_id>', views.team_detail, name="team_detail"),
    path('team-creation/', views.team_creation, name="team_creation"),
    path('logout', views.logout_action, name='logout'),
    path('join/<int:team_id>', views.join, name='join'),
    path('leave/<int:team_id>', views.leave, name='leave'),
    path('add', views.add, name='add'),
    path('team-set-profile/<int:team_id>', views.set_team_profile, name='team_set_profile'),
    path('set-member-goal/<int:runner_id>', views.set_member_goal, name='set_member_goal'),
    path('search', views.search_action, name='search'),
    path('run-search-action', views.run_search_action, name='run_search_action'),
    # path('run-search', views.run_search, name='run_search'),
    path('profile/<str:username>', views.profile, name='profile'),
    path("get_photo/<str:username>", views.get_photo, name="get_photo"), 
    path("set_picture/<str:username>", views.set_picture, name="set_picture"),
    path("set_personal_goal/<str:username>", views.set_personal_goal, name="set_personal_goal"),
    path('account', views.account_search, name='account_search'),
    path('add_run_logging', views.add_run_logging, name='add_run_logging'),
    path('del_run_logging', views.del_run_logging, name='del_run_logging'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

