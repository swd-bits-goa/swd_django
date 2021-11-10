from django.db import models
from django.utils import timezone
from datetime import datetime
from datetime import date

# Create your models here.

class InOut(models.Model):
    student = models.ForeignKey('main.Student', on_delete = models.CASCADE)
    place = models.CharField(max_length=20, null=True, blank=True)
    outDateTime = models.DateTimeField(null=True)
    inDateTime = models.DateTimeField(null=True, blank=True)
    inCampus = models.BooleanField(null=False, default=True)
    onLeave = models.BooleanField(null=False, default=False)
    onDaypass = models.BooleanField(null=False, default=False)

    def __str__(self):
        return self.student.bitsId + ' (' + self.student.name + ')'