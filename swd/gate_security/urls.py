from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView


from . import views

urlpatterns = [
    url(r'^gate_security/$', views.gate_security, name='gate_security'),
    url(r'^gate_security/in_out/$', views.in_out, name='in_out'),
    # url(r'^gate_security/defaulters/$', views.defaulters, name='defaulters'),
    url(r'^gate_security/daypasses_security/$', views.dash_security_daypass, name='daypasses_security'),
    url(r'^gate_security/security_leaves/$', views.dash_security_leaves, name='dash_security_leaves'),
    url(r'^gate_security/daypass_out/$', views.daypass_out, name='daypass_out'),
    url(r'^gate_security/leave_out/$', views.leave_out, name='leave_out'),
    url(r'^gate_security/weekend_security/$', views.dash_security_weekendpass, name='weekend_security'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

