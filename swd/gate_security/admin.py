# Register your models here.
from django.contrib import admin
from import_export.formats import base_formats
from import_export.admin import ExportMixin
from gate_security.models import InOut, WeekendPass


class InOutAdmin(ExportMixin, admin.ModelAdmin):
    search_fields = ['student__name','student__bitsId', 'inDateTime', 'onLeave', 'onDaypass']

    def get_export_formats(self):
        formats = (
            base_formats.XLS,
        )
        return [f for f in formats if f().can_export()]

class WeekendPassAdmin(admin.ModelAdmin):
    search_fields = ['student__name', 'student__bitsId', 'expiryDate']
    list_display = ('student', 'expiryDate', 'approved')

admin.site.register(InOut, InOutAdmin)
admin.site.register(WeekendPass, WeekendPassAdmin)