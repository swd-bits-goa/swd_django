import django
from django.urls import path
from django.views.i18n import JavaScriptCatalog

from jet.views import add_bookmark_view, remove_bookmark_view, toggle_application_pin_view, model_lookup_view


app_name = 'jet'

urlpatterns = [
    path(
        'add_bookmark/',
        add_bookmark_view,
        name='add_bookmark'
    ),
    path(
        'remove_bookmark/',
        remove_bookmark_view,
        name='remove_bookmark'
    ),
    path(
        'toggle_application_pin/',
        toggle_application_pin_view,
        name='toggle_application_pin'
    ),
    path(
        'model_lookup/',
        model_lookup_view,
        name='model_lookup'
    ),
    path(
        'jsi18n/',
        JavaScriptCatalog.as_view(),
        {'packages': 'django.contrib.admin+jet'},
        name='jsi18n'
    ),
]
