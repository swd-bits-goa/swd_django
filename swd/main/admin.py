from django.contrib import admin
from main.models import *
from django.utils.html import format_html
from django.core.urlresolvers import reverse
import urllib
from django.http import HttpResponseRedirect
# import django.models.queryset as QuerySet

class StudentAdmin(admin.ModelAdmin):
    search_fields = ['name','bitsId']

models = [ Faculty, Warden, Nucleus, Superintendent, FacultyIncharge, Staff, DayScholar, HostelPS, CSA, MessOption, Leave, DayPass, LateComer, InOut, Disco, MessOptionOpen, Transaction, MessBill]
    

@admin.register(Bonafide)
class BonafideAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'student',
        'reqDate',
        'printed',
        'bonafide_actions', 
    )
    def get_url(self, pk):
        url = '/bonafide/?bonafide=' + str(Bonafide.objects.get(pk=pk).id)
        return url

    def bonafide_actions(self, obj):
        return format_html  (
            '<a class="button" href="{}" target="blank_">Print</a>&nbsp;',
            self.get_url(obj.pk),
        )
    bonafide_actions.short_description = 'Bonafide Actions'
    bonafide_actions.allow_tags = True

admin.site.register(Student, StudentAdmin)
# admin.site.register(Bonafide, BonafideAdmin)
admin.site.register(models)

