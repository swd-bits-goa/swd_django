from django.db import models
from datetime import datetime
from main.models import Student
import hashlib

try:
    from tools.dev_info import SALT_IMG as SALT
except ModuleNotFoundError:
    SALT = '1234567890'


class MCNApplicationPeriod(models.Model):
    Open = models.DateTimeField()
    Close = models.DateTimeField()

    def __str__(self):
        pass

    class Meta:
        verbose_name = 'MCN Application Period'
        verbose_name_plural = 'MCN Application Periods'


class MCNApplication(models.Model):
    def document_path(instance, filename):
        ext = filename.split('.')[-1]
        tempname = (SALT+instance.student.bitsId+str(datetime)).encode('utf-8')
        return 'MCN/{}.{}'.format(
            hashlib.md5(tempname).hexdigest(), ext)

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    ApplicationPeriod = models.ForeignKey(
        MCNApplicationPeriod, on_delete=models.CASCADE)
    Filled = models.DateTimeField(blank=True)
    FathersIncome = models.IntegerField()
    MothersIncome = models.IntegerField()
    ApplicationForm = models.FileField(
        upload_to=document_path, null=True, blank=True)
    FathersIncomeDoc = models.FileField(
        upload_to=document_path, null=True, blank=True)
    MothersIncomeDoc = models.FileField(
        upload_to=document_path, null=True, blank=True)
    TehsildarCertificate = models.FileField(
        upload_to=document_path, null=True, blank=True)
    BankPassbook = models.FileField(
        upload_to=document_path, null=True, blank=True)

    def __str__(self):
        pass

    class Meta:
        verbose_name = 'MCN Application'
        verbose_name_plural = 'MCN Applications'
