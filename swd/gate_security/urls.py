from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView


from . import views

urlpatterns = [
    

url(r'^gate_security/$', views.gate_security, name='gate_security'),
url(r'^gate_security/in_out/$', views.in_out, name='in_out'),
url(r'^gate_security/daypasses_security/$', views.dash_security_daypass, name='daypasses_security'),
url(r'^gate_security/security_leaves/$', views.dash_security_leaves, name='dash_security'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

