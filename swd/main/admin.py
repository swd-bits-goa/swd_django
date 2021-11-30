from django.contrib import admin
from django.shortcuts import redirect
from main.models import *
from django.utils.html import format_html
import urllib
from django.http import HttpResponseRedirect, HttpResponse
import datetime
from .models import MessBill, Leave
from calendar import monthrange
from import_export.admin import ExportActionModelAdmin, ImportExportModelAdmin
from .resources import *


models = [
    Warden,
    Staff,
    DayScholar,
    CSA,
    LateComer,
    MessOptionOpen,
    Transaction,
    MessBill,
    TeeAdd,
    ItemAdd,
    HostelSuperintendent,
    Notice,
    FileAdd,
    Document,
    AntiRagging,
    DueCategory,
    DuesPublished,
    VacationDatesFill,
    Security]

@admin.register(Disco)
class HostelPSAdmin(admin.ModelAdmin):
    search_fields = ['student__name', 'student__bitsId']

class DiscoAdmin(admin.ModelAdmin):
    search_fields = ['student__bitsId', 'student__name']

@admin.register(DayPass)
class DayPassAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['student__bitsId', 'student__name']

@admin.register(Bonafide)
class BonafideAdmin(admin.ModelAdmin):
    search_fields = ['reason','otherReason', 'reqDate','student__name','student__bitsId']
    list_display = (
        'id',
        'student',
        'reason', 
        'reqDate',
        'printed',
        'status',
        'bonafide_actions',
    )
    list_filter = ('status',)
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

def exportmessbill_xls(modeladmin, request, queryset):
    select = [ i.student.bitsId for i in queryset]
    return HttpResponseRedirect("/messbill/?ids=%s" % (",".join(select)))
exportmessbill_xls.short_description = u"Export Mess Bill"



def update_cgpa(modeladmin, request, queryset):
    return redirect('import_cgpa')
update_cgpa.short_description = u"Update CGPAs with Excel File"

def add_new_students(modeladmin, request, queryset):
    return redirect('add_new_students')
add_new_students.description = u"Add New Students from Excel"

def delete_students(modeladmin, request, queryset):
    return redirect('delete_students')
delete_students.description = u"Delete Students from Excel"

class StudentAdmin(ExportActionModelAdmin):
    search_fields = ['name', 'bitsId', 'user__username']
    actions = [exportmessbill_xls, update_cgpa, add_new_students, delete_students ]


@admin.register(TeeBuy)
class TeeBuyAdmin(ExportActionModelAdmin, admin.ModelAdmin):
    resource_class = TeeBuyResource
    search_fields = ['tee__title']
    


@admin.register(ItemBuy)
class ItemBuyAdmin(ExportActionModelAdmin, admin.ModelAdmin):
    resource_class = ItemBuyResource  
    search_fields = ['item__title']

@admin.register(MessOption)
class MessOptionAdmin(ExportActionModelAdmin, admin.ModelAdmin):
    resource_class = MessOptionResource
    search_fields = ['mess','monthYear', 'student__bitsId']
    

@admin.register(Leave)
class LeaveAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    search_fields = ['student__name', 'student__bitsId','dateTimeStart','id', 'student__user__username', 'reason']
    actions = [exportmessbill_xls, ]
    list_display = ('student', 'reason', 'dateTimeStart')
    list_filter = ('student', 'reason')

@admin.register(Due)
class DueAdmin(admin.ModelAdmin):
    search_fields = ['student__name','amount','due_category__name','description','date_added']


admin.site.register(Student, StudentAdmin)
admin.site.register(HostelPS, HostelPSAdmin)
# admin.site.register(Bonafide, BonafideAdmin)
admin.site.register(models)
