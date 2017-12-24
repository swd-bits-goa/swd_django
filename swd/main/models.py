from django.db import models
from django.contrib.auth.models import User

MESS_CHOICES = (
    ('A','Dining Hall A'),
    ('C','Dining Hall C'))

CONSENT_CHOICES = (
    ('Letter', 'Letter'),
    ('Fax', 'Fax'),
    ('Email', 'Email'))

class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    chamber = models.CharField(max_length=10)
    residence = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    email = models.EmailField()

class Warden(models.Model):
    faculty = models.OneToOneField('Faculty', on_delete=models.CASCADE)
    hostel = models.CharField(max_length=5)

class Nucleus(models.Model):
    faculty = models.OneToOneField('Faculty', on_delete=models.CASCADE)
    function = models.CharField(max_length=20)

class Superintendent(models.Model):
    faculty = models.OneToOneField('Faculty', on_delete=models.CASCADE)
    function = models.CharField(max_length=20)

class FacultyIncharge(models.Model):
    faculty = models.OneToOneField('Faculty', on_delete=models.CASCADE)
    function = models.CharField(max_length=20)

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    staffType = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
   
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    bitsId = models.CharField(max_length=15)
    gender = models.CharField(max_length=1)
    bDay = models.DateField()
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    bloodGroup = models.CharField(max_length=10)
    cgpa = models.FloatField(null=True)
    admit = models.DateField()
    parentName = models.CharField(max_length=50)
    parentPhone = models.CharField(max_length=20)
    parentEmail = models.CharField(max_length=50)

    def __str__(self):
        return self.bitsId + ' (' + self.name + ')'

class DayScholar(models.Model):
    student = models.OneToOneField('Student', on_delete = models.CASCADE)

class HostelPS(models.Model):
    student = models.OneToOneField('Student', on_delete = models.CASCADE)
    ps = models.BooleanField()
    psStation = models.CharField(max_length=20, null=True)
    hostel = models.CharField(max_length=5, null=True)
    room = models.CharField(max_length=4, null=True)

class CSA(models.Model):
    student = models.OneToOneField('Student', on_delete = models.CASCADE)
    title = models.CharField(max_length=20)
    email = models.EmailField()

class MessOption(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    monthYear = models.DateField()
    mess = models.CharField(max_length=1, choices=MESS_CHOICES)
    
class Bonafide(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    reason = models.CharField(max_length=20)
    otherReason = models.CharField(max_length=20, null=True)
    reqDate = models.DateField()
    printed = models.BooleanField()

class Leave(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    dateTimeStart = models.DateTimeField()
    dateTimeEnd = models.DateTimeField()
    reason = models.TextField()
    consent = models.CharField(max_length=10, choices=CONSENT_CHOICES)
    corrAddress = models.TextField()
    corrPhone = models.CharField(max_length=15)
    approvedBy = models.CharField(max_length=50, default=None)
    approved = models.BooleanField(default=None)
    comment = models.TextField(default=None)

class DayPass(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    date = models.DateField()
    reason = models.TextField()
    consent = models.CharField(max_length=10)
    approvedBy = models.CharField(max_length=50)
    approved = models.BooleanField()
    comment = models.TextField()

class LateComer(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    dateTime = models.DateTimeField()

class InOut(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    place = models.CharField(max_length=20)
    outDateTime = models.DateTimeField()
    inDateTime = models.DateTimeField()
    onCampus = models.BooleanField()
    onLeave = models.BooleanField()

class Disco(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    dateOfViolation = models.DateField()
    subject = models.TextField()
    action = models.TextField()
    date = models.DateField()


class MessOptionOpen(models.Model):
    monthYear = models.DateField()
    dateOpen = models.DateField()
    dateClose = models.DateField()


class Transaction(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

class MessBill(models.Model):
    transaction = models.OneToOneField('Transaction', on_delete=models.CASCADE)
    month = models.DateField()
    amount = models.FloatField()
