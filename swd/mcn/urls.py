from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path('submit_mcn/', views.submit_mcn, name="submit_mcn"),

    path('admin/export_mcn/<int:mcn_period_pk>/<str:filter_criteria>', views.export_mcn_approved, name="export_mcn"),
]
