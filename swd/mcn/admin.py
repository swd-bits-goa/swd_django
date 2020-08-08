from django.contrib import admin

from .models import MCNApplication, MCNApplicationPeriod


admin.site.register(MCNApplication)
admin.site.register(MCNApplicationPeriod)


def download_mcn_docs(mcn_application):
    """
    Admin button to download documents in an MCN Application.
    """
    pass