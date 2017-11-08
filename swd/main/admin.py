from django.contrib import admin
from main.models import *

class StudentAdmin(admin.ModelAdmin):
    search_fields = ['name','bitsId']

models = [ Faculty, Warden, Nucleus, Superintendent, FacultyIncharge, Staff, DayScholar, HostelPS, CSA, MessOption, Bonafide, Leave, DayPass, LateComer, InOut, Disco, MessOptionOpen, Transaction, MessBill]
    
admin.site.register(Student, StudentAdmin)
admin.site.register(models)
