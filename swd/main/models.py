from django.db import models
from django.contrib.auth.models import User
import os
import hashlib
from tools.dev_info import SALT_IMG as SALT
import re
from django.utils import timezone

MESS_CHOICES = (
    ('A','Dining Hall A'),
    ('C','Dining Hall C'),
    ('D','Dining Hall D'))

CONSENT_CHOICES = (
    ('Letter', 'Letter'),
    ('Fax', 'Fax'),
    ('Email', 'Email')
    )

BONAFIDE_REASON_CHOICES = (
    ('Bank Loan', 'Bank Loan'),
    ('Passport', 'Passport'),
    ('Other', 'Other'))

BRANCH = {
    'A1': 'B.E.(Hons) Chemical Engineering',
    'A3': 'B.E.(Hons) Electrical and Electronics Engineering',
    'A4': 'B.E.(Hons) Mechanical Engineering',
    'A7': 'B.E.(Hons) Computer Science',
    'A8': 'B.E.(Hons) Electronics and Instrumentation Engineering',
    'B1': 'MSc. (Hons) Biology',
    'B2': 'MSc. (Hons) Chemistry',
    'B3': 'MSc. (Hons) Economics',
    'B4': 'MSc. (Hons) Mathematics',
    'B5': 'MSc. (Hons) Physics',
    'AA': 'B.E.(Hons) Electronics and Communication Engineering',
    'PH': 'PhD.',
    'H1': 'M.E. (Hons) Computer Science',

}

YEARNAMES = {
     1: 'first',
     2: 'second',
     3: 'third',
     4: 'forth',
     5: 'fifth',
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
    ('DH1', 'DH1'),
    ('DH2', 'DH2'),
    ('DH3', 'DH3'),
    ('DH4', 'DH4'),
)

class Warden(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=True)
    chamber = models.CharField(max_length=15, null=True, blank=True)
    residence = models.CharField(max_length=10, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    hostel = models.CharField(max_length=5, choices=HOSTELS, null=True, blank=True)

    def __str__(self):
        return self.hostel + ' ' + self.name + ' ' + self.email + ' ' + self.chamber

class HostelSuperintendent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    hostel = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.hostel + ' ' + self.name + ' ' + self.email

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    staffType = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.staffType + ' ' + self.name

class Student(models.Model):    
    def hash_upload(instance, filename):
        ext = filename.split('.')[-1]
        tempname = (SALT+instance.bitsId).encode('utf-8')
        return '{}.{}'.format(hashlib.md5(tempname).hexdigest(), ext)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    bitsId = models.CharField(max_length=15)
    gender = models.CharField(max_length=1, blank=True)
    bDay = models.DateField(blank=True, null=True)
    profile_picture=models.FileField(upload_to=hash_upload, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    bloodGroup = models.CharField(max_length=10, blank=True, null=True)
    cgpa = models.FloatField(blank=True, null=True)
    admit = models.DateField(blank=True, null=True)
    parentName = models.CharField(max_length=50, blank=True, null=True)
    parentPhone = models.CharField(max_length=20, blank=True, null=True)
    parentEmail = models.CharField(max_length=50, blank=True, null=True)

    def nophd(self):
        return re.match(r"^20\d{2}PHX[PF]\d{3,4}G$", self.bitsId, flags=re.IGNORECASE)

    def __str__(self):
        return self.bitsId + ' (' + self.name + ')'

    def change_cgpa(self, new_cg):
        if ((new_cg > 0.0) and (new_cg <= 10.0)):
            self.cgpa = new_cg
            self.save()
            return True
        else:
            return False

class DayScholar(models.Model):
    student = models.OneToOneField('Student', on_delete = models.CASCADE)

    def __str__(self):
        return self.student.bitsId + ' (' + self.student.name + ')'

class HostelPS(models.Model):
    student = models.OneToOneField('Student', on_delete = models.CASCADE, related_name='hostelps')
    acadstudent = models.BooleanField()
    status = models.CharField(max_length=10, choices=STUDENT_STATUS)
    psStation = models.CharField(max_length=100, null=True, blank=True)
    hostel = models.CharField(max_length=5, null=True, blank=True, choices=HOSTELS)
    room = models.CharField(max_length=7, null=True, blank=True)

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
    pic = models.ImageField(blank=True, null=True)
    priority=models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title + ' ' + self.student.name + ' ' + self.email

class MessOption(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    monthYear = models.DateField()
    mess = models.CharField(max_length=1, choices=MESS_CHOICES)

    def __str__(self):
        return self.mess + ' ' + self.student.bitsId

class Bonafide(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    reason = models.CharField(max_length=20, choices=BONAFIDE_REASON_CHOICES)
    otherReason = models.CharField(max_length=200, null=True, blank=True)
    reqDate = models.DateField()
    printed = models.BooleanField(default=0, blank=True)
    text = models.TextField(default='', blank=True)

    def createText(self):
        gender = "Mr. " if self.student.gender.lower() == 'm' else "Ms. "
        pronoun = "He " if gender=="Mr. " else "She "
        firstDeg=self.student.bitsId[4:6]
        secondDeg=self.student.bitsId[6:8]
        branch = BRANCH[firstDeg]
        res=HostelPS.objects.get(student=self.student)
        if secondDeg != 'PS' and firstDeg != 'H1' and firstDeg != 'PH':
            branch = branch +' and '+ BRANCH[secondDeg]
        yearNum=self.reqDate.year-int(self.student.bitsId[0:4]) + 1
        if(self.reqDate.month <5):
            yearNum=yearNum-1
        yearName=YEARNAMES[yearNum]

        reason = self.otherReason if self.reason.lower()=='other' else self.reason
        if(res.status == "Student"):
            return '''&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;This is to certify that <i>''' + gender + self.student.name.title() + '''</i>, ID No. <i>''' + self.student.bitsId + '''</i> is a bonafide student of '''+ yearName + ''' year at Birla Institute of Technology and Science (BITS) Pilani University, K.K Birla Goa campus, pursuing ''' + branch + '''. '''+pronoun+''' is residing in the Hostel <i>'''+res.hostel+'''-'''+res.room+'''</i> of this institute.''' +'''<br>This certificate is issued for the purpose of applying for ''' + reason + '''.'''
        elif(res.status == "Thesis" or res.status == "PS2"):
            return '''&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;This is to certify that <i>''' + gender + self.student.name.title() + '''</i>, ID No. <i>''' + self.student.bitsId + '''</i> is a bonafide student of '''+ yearName + ''' year class. ''' + pronoun +''' was admitted to the Institute on <i>30/07/2014</i>, for pursuing the <i>'''+ branch +'''</i> programme of studies. '''+ pronoun+ ''' is pursuing <i>''' + res.status + '''</i> at <i>'''+ res.psStation +'''</i> as a part of the academic requirement of BITS-Pilani, Deemed University.<br>This certificate is issued for the purpose of applying for ''' + reason + '''.'''

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
    approvedBy = models.ForeignKey('Warden', blank=True, null=True, on_delete="PROTECT")
    approved = models.BooleanField(default=0, blank=True)
    disapproved = models.BooleanField(default=0, blank=True)
    inprocess = models.BooleanField(default=1, blank=True)
    comment = models.TextField(default='', blank=True)

    def __str__(self):
        return self.student.bitsId + ' '+ self.student.name + ' ' + str(self.id)

class DayPass(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    reason = models.TextField()
    dateTime = models.DateTimeField(null=True)
    inTime = models.DateTimeField(null=True)
    corrAddress = models.TextField()
    approvedBy = models.ForeignKey('HostelSuperintendent', blank=True, null=True, on_delete="PROTECT")
    approved = models.BooleanField(default=0, blank=True)
    disapproved = models.BooleanField(default=0, blank=True)
    inprocess = models.BooleanField(default=1, blank=True)
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
    month = models.DateField()
    amount = models.FloatField()
    rebate = models.FloatField()

    class Meta:
        get_latest_by = "month"

    def __str__(self):
        return str(self.month) + ' ' + str(self.amount) + ' ' + str(self.rebate)

# All store options are filled here

class TeeAdd(models.Model):
    title = models.CharField(max_length=30)
    desc = models.TextField()
    pic = models.ImageField(blank=True, null=True)
    price = models.FloatField()
    nick = models.BooleanField(blank=True)
    colors = models.CharField(max_length=100, blank=True, null=True)
    sizes = models.CharField(max_length=100, blank=True, null=True)
    available = models.BooleanField(default=False)

    def __str__(self):
        return self.title + ' - Rs.' + str(self.price)

class ItemAdd(models.Model):
    title = models.CharField(max_length=30)
    desc = models.TextField()
    pic = models.ImageField(blank=True, null=True)
    price = models.FloatField()
    available = models.BooleanField(default=False)

    def __str__(self):
        return self.title + ' - Rs.' + str(self.price)

class TeeBuy(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    tee = models.ForeignKey('TeeAdd', on_delete = models.CASCADE)
    qty = models.IntegerField()
    nick = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=10, blank=True, null=True)
    size = models.CharField(max_length=10, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    totamt = models.FloatField()

    def __str__(self):
        return self.student.bitsId + ' ' + self.tee.title

    def save(self, *args, **kwargs):
        self.totamt = float(self.qty) * float(self.tee.price)
        super(TeeBuy, self).save(*args, **kwargs)
  
class ItemBuy(models.Model):
    student = models.ForeignKey('Student', on_delete = models.CASCADE)
    item = models.ForeignKey('ItemAdd', on_delete = models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.student.bitsId + ' ' + self.item.title

class DueCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)

    def __str__(self):
        return "Due category with name {} and description '{}'".format(self.name, self.description)

class Due(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.FloatField()
    due_category = models.ForeignKey(DueCategory, on_delete=models.CASCADE)
    description = models.CharField(max_length=500)
    date_added = models.DateField()

    class Meta:
        verbose_name_plural = "Dues"

    def __str__(self):
        return self.student.bitsId + "'s due entry with amount " + str(self.amount)

class DuesPublished(models.Model):
    # This model keeps track of when dues was completely up to date
    # last time.
    date_published = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.date_published)

class FileAdd(models.Model):

    file = models.FileField()
    link = models.CharField(max_length=200, blank=True, null=True, editable = False, default='/')

    def __str__(self):
        return self.link

    def save(self, *args, **kwargs):
        self.link = '/media/' + self.file.name 
        super().save(*args, **kwargs)


class Notice(models.Model):
    
    date = models.DateField(editable=False) 
    title = models.CharField(max_length=100)
    desc = models.TextField()
    file = models.ForeignKey(FileAdd, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.desc
    def save(self, *args, **kwargs):
        self.date = timezone.now()
        super().save(*args, **kwargs)


class Document(models.Model):
    title = models.CharField(max_length=100)
    #file = models.ForeignKey(FileAdd, on_delete=models.CASCADE, null=True, blank=True)
    link = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return self.title    
class AntiRagging(models.Model):
    title = models.CharField(max_length=100)
    link = models.CharField(max_length=100)

    def __str__(self):
        return self.title  


class VacationDatesFill(models.Model):
    """
    Opens option for Students to fill vacation details.
    Creates Leave objects that do not require Warden approval.
    """
    description = models.CharField(max_length=50)
    dateOpen = models.DateField(
        help_text="Students can start filling details from this date (inclusive)")
    dateClose = models.DateField(
        help_text="Students can fill details only before this date (inclusive)")
    allowDateAfter = models.DateTimeField(
        help_text="Allowed Vacation Dates start from this date (inclusive)")
    allowDateBefore = models.DateTimeField(
        help_text="Allowed Vacation Dates end before this (inclusive)")
    messOption = models.ForeignKey(
        MessOptionOpen,
        on_delete=models.CASCADE,
        default=None,
        help_text="Mess Option for the months near corresponding Vacation")

    class Meta:
        verbose_name = "Vacation Dates Option"
        verbose_name_plural = "Vacation Dates Option"

    def __str__(self):
        return str(self.description) + ' Open: ' + str(self.dateOpen) + ' Close: ' + str(self.dateClose)

    def check_student_valid(self, student):
        """
        Checks whether the student has already filled vacation details.
        """
        leaves_count = Leave.objects.filter(
            student=student,
            dateTimeStart__gte=self.allowDateAfter,
            dateTimeEnd__lte=self.allowDateBefore
            ).count()
        if leaves_count == 0:
            return True
        else:
            return False

    def create_vacation(self, student, dateTimeStart, dateTimeEnd):
        """
        Create Leave Objects for the Vacation

        param:
        student : Student Object
        data : python dictionary
        
        returns:
        True, obj :  when object created
        False, error: when no object created, error is a str
        """
        try:
            leave = Leave(student=student, reason=self.description)
            leave.dateTimeStart = dateTimeStart
            leave.dateTimeEnd = dateTimeEnd
            leave.approved = True
            leave.disapproved = False
            leave.inprocess = False
            leave.comment = "Vacation"
            leave.save()
            return True, leave
        except Exception as e:
            return False, str(e)
    
    def check_date_in_range(self, date):
        """
        Checks whether the date is between allowDateAfter and allowDateBefore

        params:
        date: datetime object
        """
        if date.date() <= self.allowDateBefore.date() \
            and date.date() >= self.allowDateAfter.date():
            return True
        else:
            return False
    
    def check_start_end_dates_in_range(self, dateTimeStart, dateTimeEnd):
        """
        Checks whether both start and end date time objects are in range
            and start date less than end date

        params:
        dateTimeStart, dateTimeEnd: datetime object
        """
        first_cond = self.check_date_in_range(dateTimeStart) and \
            self.check_date_in_range(dateTimeEnd)
        return first_cond and dateTimeStart < dateTimeEnd

    def check_student_filled_details(self, student):
        """
        Checks whether the student has already filled the details and
            leave object is present in database.
        """
        objs = Leave.objects.filter(
            student=student, reason=self.description, comment="Vacation")
        return objs.count() > 0


class AddressChangeRequest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    new_address = models.TextField()
    approved = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)

    def approve(self):
        self.student.address = self.new_address
        self.approved = True
        self.resolved = True
        self.student.save()
        self.save()

    def reject(self):
        self.approved = False
        self.resolved = True
        self.student.save()
        self.save()

