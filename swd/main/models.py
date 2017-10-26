from django.db import models

class Login(models.Model):
    loginId = models.CharField(max_length=10)

class Faculty(models.Model):
    login = models.OneToOneField('Login', on_delete=models.CASCADE)
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
   
class Student(models.Model):
    login = models.OneToOneField('Login', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    bitsId = models.CharField(max_length=15)
    gender = models.CharField(max_length=1)
    bDay = models.DateField()
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    bloodGroup = models.CharField(max_length=3)
    cgpa = models.FloatField()
    admit = models.DateField()
    parentName = models.CharField(max_length=50)
    parentPhone = models.CharField(max_length=20)
    parentEmail = models.CharField(max_length=50)

class DayScholar(models.Model):
    student = models.OneToOneField('Student', on_delete = models.CASCADE)

class hostelPS(models.Model):
    student = models.OneToOneField('Student', on_delete = models.CASCADE)
    ps = models.BooleanField()
    psStation = models.CharField(max_length=20)
    hostel = models.CharField(max_length=5, null=True)
    room = models.CharField(max_length=4, null=True)

class CSA(models.Model):
    student = models.OneToOneField('Student', on_delete = models.CASCADE)
    title = models.CharField(max_length=20)
    email = models.EmailField()

class MessOption(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    monthYear = models.DateField()
    mess = models.CharField(max_length=1)
    
class Bonafide(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    reason = models.CharField(max_length=20)
    otherReason = models.CharField(max_length=20, null=True)
    reqDate = models.DateField()
    printed = models.BooleanField()

class Leave(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    dateTimeStart = models.DateTimeField()
    dataTimeEnd = models.DateTimeField()
    reason = models.TextField()
    consent = models.CharField(max_length=10)
    corrAddress = models.TextField()
    corrPhone = models.CharField(max_length=15)


