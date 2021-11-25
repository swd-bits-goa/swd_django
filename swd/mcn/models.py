from django.db import models
from datetime import datetime
import hashlib

try:
    from tools.dev_info import SALT_IMG as SALT
except ModuleNotFoundError:
    SALT = '1234567890'


class MCNApplicationPeriod(models.Model):
    """
    Stores time period when MCN Application portals were opened and closed.
    """
    Open = models.DateTimeField(default=None)
    Close = models.DateTimeField(default=None)
    Name = models.TextField("Application Period Name", default="Semester X 2020-21")
    Batch = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.Name + ": " + self.Open.strftime('%d-%b-%Y') + \
            ' to ' + self.Close.strftime('%d-%b-%Y')

    class Meta:
        verbose_name = 'MCN Application Period'
        verbose_name_plural = 'MCN Application Periods'


class MCNApplication(models.Model):
    """
    Stores MCN Application of a single student with the documents.
    """

    def document_path(instance, filename):
        ext = filename.split('.')[-1]
        name = filename.split('.')[0]
        tempname = (SALT + instance.student.bitsId +
                    str(instance.DateTimeSubmitted) + name).encode('utf-8')
        return 'MCN/{}.{}'.format(
            hashlib.md5(tempname).hexdigest(), ext)

    student = models.ForeignKey('main.Student', on_delete=models.CASCADE, default=None)
    ApplicationPeriod = models.ForeignKey(
        'MCNApplicationPeriod', on_delete=models.CASCADE, default=None)
    DateTimeSubmitted = models.DateTimeField(auto_now=True)
    FathersIncome = models.IntegerField(default=0)
    MothersIncome = models.IntegerField(default=0)
    FathersIncomeDoc = models.FileField(
        upload_to=document_path, null=True, blank=True)
    MothersIncomeDoc = models.FileField(
        upload_to=document_path, null=True, blank=True)
    TehsildarCertificate = models.FileField(
        upload_to=document_path, null=True, blank=True)
    BankPassbook = models.FileField(
        upload_to=document_path, null=True, blank=True)
    approved = models.BooleanField("Approve Application", default=False)
    rejected = models.BooleanField("Reject Application", default=False)
    MothersName = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.student.name + ': ' + self.DateTimeSubmitted.strftime('%Y-%m-%d')

    class Meta:
        verbose_name = 'MCN Application'
        verbose_name_plural = 'MCN Applications'
