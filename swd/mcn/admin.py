from django.contrib import admin

from .models import MCNApplication, MCNApplicationPeriod

admin.site.register(MCNApplicationPeriod)

@admin.register(MCNApplication)
class MCNApplicationAdmin(admin.ModelAdmin):
    search_fields = ['student__name', 'student__bitsId']
    list_display = (
        'student',
        'ApplicationPeriod',
        'approved'
    )
