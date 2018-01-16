from django.db import models
from django.contrib.auth.models import User

MESS_CHOICES = (
    ('A','Dining Hall A'),
    ('C','Dining Hall C'))

CONSENT_CHOICES = (
    ('Letter', 'Letter'),
    ('Fax', 'Fax'),
    ('Email', 'Email'))

BONAFIDE_REASON_CHOICES = (
    ('Bank Loan', 'Bank Loan'),
    ('Fax', 'Fax'),
    ('Other', 'Other'))

BRANCH = {
    'A1': 'B.E.(Hons) Chemical Engineering',
    'A3': 'B.E.(Hons) Electrical and Electronics Engineering',
    'A4': 'B.E.(Hons) Mechanical Engineering',
    'A7': 'B.E.(Hons) Computer Science',
    'A8': 'B.E.(Hons) Electronics and Instrumentation Engineering',
}

STUDENT_STATUS = (
    ('Student', 'Student'),
    ('Thesis', 'Thesis'),
    ('PS2', 'PS2'),
    ('Graduate', 'Graduate'))

HOSTELS = (
    ('AH1', 'AH1'),
    ('AH2', 'AH2'),
    ('AH3', 'AH3'),
    ('AH4', 'AH4'),
    ('AH5', 'AH5'),
    ('AH6', 'AH6'),
    ('AH7', 'AH7'),
    ('AH8', 'AH8'),
    ('AH9', 'AH9'),
    ('CH1', 'CH1'),
    ('CH2', 'CH2'),
    ('CH3', 'CH3'),
    ('CH4', 'CH4'),
    ('CH5', 'CH5'),
    ('CH6', 'CH6'),
    ('CH7', 'CH7'),
)

class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    chamber = models.CharField(max_length=10)
    residence = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return self.name + ' ' + self.email + ' ' + self.chamber

class Warden(models.Model):
    faculty = models.OneToOneField('Faculty', on_delete=models.CASCADE)
    hostel = models.CharField(max_length=5, choices=HOSTELS)

    def __str__(self):
        return self.hostel + ' ' + self.faculty.name + ' ' + self.faculty.email + ' ' + self.faculty.chamber

class Nucleus(models.Model):
    faculty = models.OneToOneField('Faculty', on_delete=models.CASCADE)
    function = models.CharField(max_length=20)

    def __str__(self):
        return self.function + ' ' + self.faculty.name + ' ' + self.faculty.email + ' ' + self.faculty.chamber

class Superintendent(models.Model):
    faculty = models.OneToOneField('Faculty', on_delete=models.CASCADE)
    function = models.CharField(max_length=20)

    def __str__(self):
        return self.function + ' ' + self.faculty.name + ' ' + self.faculty.email + ' ' + self.faculty.chamber

class FacultyIncharge(models.Model):
    faculty = models.OneToOneField('Faculty', on_delete=models.CASCADE)
    function = models.CharField(max_length=20)

    def __str__(self):
        return self.function + ' ' + self.faculty.name + ' ' + self.faculty.email + ' ' + self.faculty.chamber



class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    staffType = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.staffType + ' ' + self.name

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    bitsId = models.CharField(max_length=15)
    gender = models.CharField(max_length=1, blank=True)
    bDay = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    bloodGroup = models.CharField(max_length=10, blank=True, null=True)
    cgpa = models.FloatField(blank=True, null=True)
    admit = models.DateField(blank=True, null=True)
    parentName = models.CharField(max_length=50, blank=True, null=True)
    parentPhone = models.CharField(max_length=20, blank=True, null=True)
    parentEmail = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.bitsId + ' (' + self.name + ')'

class DayScholar(models.Model):
    student = models.OneToOneField('Student', on_delete = models.CASCADE)

    def __str__(self):
        return self.student.bitsId + ' (' + self.student.name + ')'

class HostelPS(models.Model):
    student = models.OneToOneField('Student', on_delete = models.CASCADE)
    acadstudent = models.BooleanField()
    status = models.CharField(max_length=10, choices=STUDENT_STATUS)
    psStation = models.CharField(max_length=20, null=True, blank=True)
    hostel = models.CharField(max_length=5, null=True, blank=True, choices=HOSTELS)
    room = models.CharField(max_length=4, null=True, blank=True)

    def __str__(self):
        return self.student.bitsId + ' (' + self.student.name + ')'

    def save(self, *args, **kwargs):
        if self.acadstudent == True:
            self.status = 'Student'
        super(HostelPS, self).save(*args, **kwargs)

class CSA(models.Model):
    student = models.OneToOneField('Student', on_delete = models.CASCADE)
    title = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.title + ' ' + self.student.name + self.email

class MessOption(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    monthYear = models.DateField()
    mess = models.CharField(max_length=1, choices=MESS_CHOICES)

    def __str__(self):
        return self.mess + ' ' + self.student.bitsId

class Bonafide(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    reason = models.CharField(max_length=20, choices=BONAFIDE_REASON_CHOICES)
    otherReason = models.CharField(max_length=20, null=True, blank=True)
    reqDate = models.DateField()
    printed = models.BooleanField(default=0, blank=True)
    text = models.TextField(default='', blank=True)

    def createText(self):
        gender = "Mr." if self.student.gender == 'M' else "Ms."
        branch = BRANCH[self.student.bitsId[4:6]]
        reason = self.reason if self.reason is not 'Other' else self.otherReason
        return '''This is to certify that ''' + gender + self.student.name.title() + ''', ID No.''' + self.student.bitsId + ''' is a bonafide student of third year class. He was admitted to the Institute on 30/07/2015, for pursuing the ''' + branch + ''' programme of studies. He is residing in the Hostel AH4 - 206 of this Institute. Date of joining the current academic session is 1 August, 2017.

    This certificate is issues for the purpose of applying for ''' + reason + ''' from 11th December 2017 to 16th December 2017 and he needs to return back to Campus on 6th January 2018 to attend his regular classes.'''

    def save(self, *args, **kwargs):
        if self.text == '':
            self.text = self.createText()
        super(Bonafide, self).save(*args, **kwargs)

    def __str__(self):
        return self.student.bitsId + ' (' + self.student.name + ') ' + self.reason

class Leave(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    dateTimeStart = models.DateTimeField()
    dateTimeEnd = models.DateTimeField()
    reason = models.TextField()
    consent = models.CharField(max_length=10, choices=CONSENT_CHOICES)
    corrAddress = models.TextField()
    corrPhone = models.CharField(max_length=15)
    approvedBy = models.ForeignKey('Warden', blank=True, null=True)
    approved = models.BooleanField(default=0, blank=True)
    disapproved = models.BooleanField(default=0, blank=True)
    inprocess = models.BooleanField(default=1, blank=True)
    comment = models.TextField(default='', blank=True)

    def __str__(self):
        return self.student.bitsId + ' '+ self.student.name

class DayPass(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    date = models.DateField()
    reason = models.TextField()
    consent = models.CharField(max_length=10)
    approvedBy = models.ForeignKey('Warden', blank=True, null=True)
    approved = models.BooleanField(default=0, blank=True)
    comment = models.TextField()

    def __str__(self):
        return self.student.bitsId + ' (' + self.student.name + ')'

class LateComer(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    dateTime = models.DateTimeField()

    def __str__(self):
        return self.student.bitsId + ' (' + self.student.name + ')'

class InOut(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    place = models.CharField(max_length=20)
    outDateTime = models.DateTimeField()
    inDateTime = models.DateTimeField()
    onCampus = models.BooleanField()
    onLeave = models.BooleanField()

    def __str__(self):
        return self.student.bitsId + ' (' + self.student.name + ')'

class Disco(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    dateOfViolation = models.DateField()
    subject = models.TextField()
    action = models.TextField()
    date = models.DateField()

    def __str__(self):
        return self.student.bitsId + ' (' + self.student.name + ')'


class MessOptionOpen(models.Model):
    monthYear = models.DateField()
    dateOpen = models.DateField()
    dateClose = models.DateField()

    def __str__(self):
        return str(self.monthYear.month) + ' Open: ' + str(self.dateOpen) + ' Close: ' + str(self.dateClose)


class Transaction(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.timestamp + ' ' + student.user

class MessBill(models.Model):
    transaction = models.OneToOneField('Transaction', on_delete=models.CASCADE)
    month = models.DateField()
    amount = models.FloatField()

    def __str__(self):
        return
