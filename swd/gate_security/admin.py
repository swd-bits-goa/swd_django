# Register your models here.
from django.contrib import admin
from gate_security.models import InOut, WeekendPass


class InOutAdmin(admin.ModelAdmin):
    search_fields = ['student__name','student__bitsId', 'inDateTime', 'onLeave', 'onDaypass']

class WeekendPassAdmin(admin.ModelAdmin):
    search_fields = ['student__name', 'student__bitsId', 'expiryDate']
    list_display = ('student', 'expiryDate', 'approved')

admin.site.register(InOut, InOutAdmin)
admin.site.register(WeekendPass, WeekendPassAdmin)


