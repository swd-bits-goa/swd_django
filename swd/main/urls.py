from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView


from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    # Django Login
    url(r'^login/', views.loginform, name="login"),
    url(r'^logout/', views.logoutform, name="logout"),

    #login_success
    url(r'^accounts/profile/', views.login_success, name='login-success'),


    url(r'^dashboard/', views.dashboard, name="dashboard"),
    url(r'^profile/', views.profile, name="profile"),
    url(r'^messoption/', views.messoption, name="messoption"),
    url(r'^leave/', views.leave, name="leave"),
    url(r'^certificates/', views.certificates, name="certificates"),
    url(r'^bonafidepdf/', views.bonafidepdf, name="bonafidepdf"),

    url(r'^warden/$', views.warden, name="warden"),
    url(r'^warden/([0-9]+)/$', views.wardenapprove, name="wardenapprove"),
    url(r'^daypass/', views.daypass, name="daypass"),
    

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
