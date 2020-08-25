from django.contrib import admin
from django.utils.html import format_html

from .models import MCNApplication, MCNApplicationPeriod


@admin.register(MCNApplicationPeriod)
class MCNApplicationPeriodAdmin(admin.ModelAdmin):
    list_display = (
        'Name',
        'Open',
        'Close',
        'actions_html'
    )

    def actions_html(self, obj):
        return format_html(
            '<button class="button" type="button" onclick="window.location.href=\'/admin/export_mcn/{pk}\'">Approved</button>'
            '<button class="button" type="button" onclick="window.location.href=\'/admin/export_mcn/{pk}/0\'">Rejected</button>', pk=obj.pk)
    actions_html.allow_tags = True
    actions_html.short_description = "Export to Excel"

@admin.register(MCNApplication)
class MCNApplicationAdmin(admin.ModelAdmin):
    search_fields = ['student__name', 'student__bitsId']
    list_display = (
        'student',
        'ApplicationPeriod',
        'approved',
        'rejected'
    )
    list_filter = (
        ('approved'),
        ('rejected')
    )
