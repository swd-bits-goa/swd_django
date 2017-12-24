"""swd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from tools import user, profile
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from main import views as main_views
from graphene_django.views import GraphQLView
from schema.schema import schema

urlpatterns = [
    url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    url(r'^admin/', admin.site.urls),
    url(r'^graphql', GraphQLView.as_view(graphiql=True, schema=schema)),
    # url(r'^login/', auth_views.login, {'template_name': 'admin/login.html'}),
    url(r'^login/', main_views.loginform, name="login"),
    url(r'^logout/', main_views.logoutform, name="logout"),
    url(r'^', include('main.urls')),
    url(r'^create-users/', user.index, name='user'),
    url(r'^create-profiles/', profile.index, name='profile'),
    url(r'^accounts/profile/', main_views.login_success, name='login-success'),
    url(r'^dashboard/', main_views.dashboard, name="dashboard"),
    url(r'^profile/', main_views.profile, name="profile"),
    url(r'^messoption/', main_views.messoption, name="messoption"),
    url(r'^leave/', main_views.leave, name="leave"),
    url(r'^certificates/', main_views.certificates, name="certificates")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
