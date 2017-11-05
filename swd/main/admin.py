from django.contrib import admin
from main.models import Student

class StudentAdmin(admin.ModelAdmin):
    search_fields = ['name','bitsId']
    
admin.site.register(Student, StudentAdmin)
