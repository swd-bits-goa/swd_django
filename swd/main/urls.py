from django.conf.urls import include, url
from django.contrib import admin
from tools import user, profile
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView


# REST
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token
from rest_framework_jwt.views import verify_jwt_token

from . import views
from .views import HelloPDFView

urlpatterns = [
    url(r'^$', views.index, name='index'),

    # Django Login
    url(r'^login/', views.loginform, name="login"),
    url(r'^logout/', views.logoutform, name="logout"),

    #login_success
    url(r'^accounts/profile/', views.login_success, name='login-success'),

    #REST
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),
    url(r'^api-token-verify/', verify_jwt_token),

    url(r'^dashboard/', views.dashboard, name="dashboard"),
    url(r'^profile/', views.profile, name="profile"),
    url(r'^messoption/', views.messoption, name="messoption"),
    url(r'^leave/', views.leave, name="leave"),
    url(r'^certificates/', views.certificates, name="certificates"),
    url(r'^bonafidepdf/', views.bonafidepdf, name="bonafidepdf"),

    url('bonafide/', HelloPDFView.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
