# Register your models here.
from django.contrib import admin
from gate_security.models import *


models = [InOut,]

class InOutAdmin(admin.ModelAdmin):
    search_fields = ['student__name']


admin.site.register(InOut, InOutAdmin)
