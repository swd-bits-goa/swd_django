import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swd.settings')

import django
django.setup()

from django.contrib.auth.models import User
from django.conf import settings
from main.models import Student, Leave, MessOption, Bonafide, Warden, HostelPS, CSA
from django.utils import timezone

import random
import datetime
import argparse

boolen_choices = [True, False]
gender_choices = ['M', 'F']
branch_choices = ['A1', 'A3', 'A4', 'A7', 'A8', 'B1', 'B2', 'B3', 'B4', 'B5']
hostel_choices = ['AH1', 'AH2', 'AH3', 'AH4', 'AH5', 'AH6', 'AH7', 'AH8', 'AH9',
                  'CH1', 'CH2', 'CH3', 'CH4', 'CH5', 'CH6', 'CH7',
                  'DH1', 'DH2', 'DH3', 'DH4']
mess_choices = ['A', 'C', 'D']
bonafide_choices = ['Bank Loan', 'Passport']
status_choices = ['Student', 'Thesis', 'PS2', 'Graduate']
bDay_start = datetime.datetime(1998, 1, 1)
bDay_end = datetime.datetime(2001, 1, 1)


def fake_number_generator(digits=10, msb=9):
    fake_number = msb
    for x in range(1, digits):
        fake_number = fake_number * 10 + random.randint(0, 10)
    return fake_number


def fake_date(start=bDay_start, end=bDay_end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return (start + datetime.timedelta(seconds=random_second)).date()


def fake_boolean():
    return random.choice(boolen_choices)


def fake_bonafide():
    return random.choice(bonafide_choices)


def fake_gender():
    return random.choice(gender_choices)


def fake_mess():
    return random.choice(mess_choices)


def fake_hostel():
    return random.choice(hostel_choices)


def fake_cgpa():
    cgpa = float(random.randrange(0, 1000)) / 100
    return cgpa

def fake_status():
    return random.choice(status_choices)

def fake_bitsID(username):
    year = username[1:5]
    uid = username[5:]
    branch = str(random.choice(branch_choices))
    return str(year + branch + 'PS' + uid + 'G')


def fake_phd(username):
    year = username[1:5]
    uid = username[5:]
    branch = 'PHX' + str(random.choice(['P', 'F']))
    return str(year + branch + uid + 'G')


def create_super_user():
    try:
        (super_user, created) = User.objects.get_or_create(username="admin", is_superuser=True)
        super_user.set_password('password')
        super_user.is_staff = True
        super_user.is_admin = True
        super_user.is_superuser = True
        super_user.save()
        print("Superuser created.")
    except:
        print("Error occurred while creating superuser.")


def create_student(i):
    try:
        fake_id = fake_bitsID if random.random() < 0.6 else fake_phd
        prefix = 'f' if fake_id == fake_bitsID else 'p'
        (mUser, created1) = User.objects.get_or_create(
            username=prefix + str(i),
            first_name='Student' + str(i),
            email=prefix + str(i) +"@goa.bits-pilani.ac.in")
        mUser.set_password('password')
        mUser.save()
        
        if created1:
            mStudent = Student(
                user=mUser,
                name='Student ' + str(i),
                bitsId=fake_id(mUser.username),
                phone=fake_number_generator(),
                gender=fake_gender(),
                bDay=fake_date(),
                email=mUser.email,
                address='BITS Goa',
                bloodGroup='O+ve',
                cgpa=fake_cgpa(),
                admit=datetime.datetime.now(),
                parentName='Parent' + str(i),
                parentPhone=fake_number_generator(),
                bank_account_no=fake_number_generator(),
            )
            mStudent.save()
            return True
    except Exception as e:
        print("Exception raised in creating student " + str(i) + ": " + str(e))
    return False


def create_hostel(i, student):
    try:
        stat = fake_status()
        hostel = ''
        room = ''
        psstation = ''
        acadstudent= False
        if stat == 'Student':
            hostel = fake_hostel()
            room = fake_number_generator(3,1)
            acadstudent = True
        elif stat == 'Thesis':
            hostel = ''
            room = ''
            psstation = 'thesis station here'
        elif stat == 'PS2':
            hostel = ''
            room = ''
            psstation = 'ps station here'
        elif stat == 'Graduate':
            hostel = 'Graduate'

        mHostel = HostelPS(
            student=student,
            acadstudent=acadstudent,
            status=stat,
            psStation = psstation,
            hostel=hostel,
            room=room,
        )
        mHostel.save()
        return True
    except Exception as e:
        print("Exception raised in creating hostel " + str(i) + ' for ' + \
            str(student) + ": " + str(e))
    return False


def create_mess(i, student):
    try:
        mMess = MessOption(
            student=student,
            monthYear=timezone.now().date(),
            mess=fake_mess()
        )
        mMess.save()
        return True
    except Exception as e:
        print("Exception raised in creating Mess Option " + str(i) + ' for ' + \
            str(student) + ": " + str(e))
    return False


def create_bonafide(i, student):
    try:
        mBonafide = Bonafide(
            student=student,
            reason=fake_bonafide(),
            reqDate=timezone.now(),
        )
        mBonafide.save()
        return True
    except Exception as e:
        print("Exception raised in creating Bonafide " + str(i) + ' for ' + \
            str(student) + ": " + str(e))
    return False


def create_leave(i, student, warden):
    try:
        status = fake_boolean()
        mLeave = Leave(
            student=student,
            dateTimeStart=timezone.now() + datetime.timedelta(days=1),
            dateTimeEnd=timezone.now() + datetime.timedelta(days=5),
            reason='SomeRandomEventDescription',
            consent='Email',
            corrAddress='Earth',
            corrPhone=fake_number_generator(),
            approvedBy=warden,
            approved=status,
            disapproved=not status,
            inprocess=not status,
        )
        mLeave.save()
        return True
    except Exception as e:
        print("Exception raised in creating leave " + str(i) + ' for ' + \
            str(student) + ": " + str(e))
    return False



def create_warden(i):
    try:
        (mUser, created1) = User.objects.get_or_create(
            username='warden' + str(i),
            first_name='Warden' + str(i),
            email='warden' + str(i) +"@goa.bits-pilani.ac.in")
        mUser.set_password('password')
        mUser.save()
        if created1:
            mStudent = Warden(
                user=mUser,
                name='Warden' + str(i),
                chamber='BX12',
                residence='D111',
                phone_off=fake_number_generator(),
                phone_res=fake_number_generator(),
                email=mUser.email,
                hostel=hostel_choices[i],
            )
            mStudent.save()
            return True
    except Exception as e:
        print("Exception raised in creating warden " + str(i) + ": " + str(e))
    return False

def create_csa(i, student):
    try:
        mcsa = CSA(
            student=student,
            title='President',
            email='prez@goa.bits-pilani.ac.in',
            pic = '2017A4PS0590_bsKDJSY.jpg',
            priority = i + 1
        )
        mcsa.save()
        return True
    except Exception as e:
        print("Exception raised in creating csa member " + str(i) + ": " + str(e))
    return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--id_start', type=int, default=20180001,
                    help='Student ID Range Start')
    parser.add_argument('--id_end', type=int, default=20180520,
                    help='Student ID Range End')
    parser.add_argument('--id_jump', type=int, default=2,
                    help='Skip this many number of IDs when creating')

    args = parser.parse_args()

    agreed = input("THIS WILL CLEAR ALL THE EXISTING DATABASE RECORDS. Continue? [Y/n]: ")
    if agreed in ['Y', 'y', 'YES']:
        print("Clearing existing database....")
    else:
        print("Exiting")
        exit()
    
    Leave.objects.all().delete()
    HostelPS.objects.all().delete()
    MessOption.objects.all().delete()
    Bonafide.objects.all().delete()
    Student.objects.all().delete()
    Warden.objects.all().delete()
    User.objects.all().delete()
    CSA.objects.all().delete()

    print("Generating the fake data now....")
    
    create_super_user()

    student_success = True
    for i in range(args.id_start, args.id_end, args.id_jump):
        student_success &= create_student(i)
    if student_success:
        print(str(1 + (args.id_end - args.id_start) // args.id_jump) + " Students created.")

    warden_success = True
    for i in range(len(hostel_choices)):
        warden_success &= create_warden(i)
    if warden_success:
        print(str(i) + " Wardens created.")

    hostel_success = True
    students_list = Student.objects.all()
    i = 0
    for student in students_list:
        hostel_success &= create_hostel(i, student)
        i += 1
    if hostel_success:
        print(str(i) + " hostelPS created.")

    mess_success = True
    i = 0
    for student in students_list:
        mess_success &= create_mess(i, student)
        i += 1
    if mess_success:
        print(str(i) + " Mess Options created.")

    bonafide_success = True
    i = 0
    for student in students_list:
        bonafide_success &= create_bonafide(i, student)
        i += 1
    if bonafide_success:
        print(str(i) + " Bonafides created.")

    leave_success = True
    i = 0
    for student in students_list:
        hostel = HostelPS.objects.get(student=student)
        if hostel.hostel in hostel_choices:
            warden = Warden.objects.get(hostel=hostel.hostel)
            leave_success &= create_leave(i, student, warden)
            i += 1
    if leave_success:
        print(str(i) + " Leaves created.")

    csa_success = True
    i = 0
    for student in students_list:
        if i<5:
            csa_success &= create_csa(i, student)
            i += 1
    if csa_success:
        print(str(i) + " Csa Members created.")


    print("Data Population Completed")
