from django.contrib import admin
from main.models import *
from django.utils.html import format_html
import urllib
from django.http import HttpResponseRedirect, HttpResponse
import datetime
from .models import MessBill, Leave
from calendar import monthrange
# import django.models.queryset as QuerySet

class HostelPSAdmin(admin.ModelAdmin):
    search_fields = ['student__name', 'student__bitsId']

models = [Warden, Staff, DayScholar, CSA, MessOption, Leave, DayPass, LateComer, InOut, Disco, MessOptionOpen, Transaction, MessBill]


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
        url = '/bonafide/' + str(Bonafide.objects.get(pk=pk).id)
        return url

    def bonafide_actions(self, obj):
        return format_html  (
            '<a class="button" href="{}" target="blank_">Print</a>&nbsp;',
            self.get_url(obj.pk),
        )
    bonafide_actions.short_description = 'Bonafide Actions'
    bonafide_actions.allow_tags = True

def export_xls(modeladmin, request, queryset):
    select = [ i.bitsId for i in queryset]
    return HttpResponseRedirect("/messbill/?ids=%s" % (",".join(select)))


export_xls.short_description = u"Export Mess Bill"

class StudentAdmin(admin.ModelAdmin):
    search_fields = ['name', 'bitsId']
    actions = [export_xls, ]

admin.site.register(Student, StudentAdmin)
admin.site.register(HostelPS, HostelPSAdmin)
# admin.site.register(Bonafide, BonafideAdmin)
admin.site.register(models)
