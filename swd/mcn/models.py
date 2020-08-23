from django.db import models
from datetime import datetime
from main.models import Student
import hashlib

try:
    from tools.dev_info import SALT_IMG as SALT
except ModuleNotFoundError:
    SALT = '1234567890'


class MCNApplicationPeriod(models.Model):
    """
    Stores time period when MCN Application portals were opened and closed.
    """
    Open = models.DateTimeField()
    Close = models.DateTimeField()

    def __str__(self):
        return self.Open.strftime('%Y-%m-%d') + '-' + self.Close.strftime('%Y-%m-%d')

    class Meta:
        verbose_name = 'MCN Application Period'
        verbose_name_plural = 'MCN Application Periods'


class MCNApplication(models.Model):
    """
    Stores MCN Application of a single student with the documents.
    """

    def document_path(instance, filename):
        ext = filename.split('.')[-1]
        tempname = (SALT+instance.student.bitsId +
                    str(datetime.now())).encode('utf-8')
        return 'MCN/{}.{}'.format(
            hashlib.md5(tempname).hexdigest(), ext)

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    ApplicationPeriod = models.ForeignKey(
        MCNApplicationPeriod, on_delete=models.CASCADE)
    DateTimeSubmitted = models.DateTimeField(blank=True)
    FathersIncome = models.IntegerField()
    MothersIncome = models.IntegerField()
    FathersIncomeDoc = models.FileField(
        upload_to=document_path, null=True, blank=True)
    MothersIncomeDoc = models.FileField(
        upload_to=document_path, null=True, blank=True)
    TehsildarCertificate = models.FileField(
        upload_to=document_path, null=True, blank=True)
    BankPassbook = models.FileField(
        upload_to=document_path, null=True, blank=True)

    def __str__(self):
        return self.student.name + ' ' + (datetime.now()).strftime('%Y-%m-%d')

    class Meta:
        verbose_name = 'MCN Application'
        verbose_name_plural = 'MCN Applications'
