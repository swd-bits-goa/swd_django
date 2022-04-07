import os
import time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swd.settings')

import django
django.setup()

from django.contrib.auth.models import User
from django.conf import settings
from main.models import Student, Leave, MessOption, Bonafide, Warden, HostelPS, CSA, Security, HostelSuperintendent, Notice
from django.utils import timezone
from django.db import transaction

import random
import datetime
import argparse

boolen_choices = [True, False]
gender_choices = ['M', 'F']
branch_choices = ['A1', 'A3', 'A4', 'A7', 'A8', 'B1', 'B2', 'B3', 'B4', 'B5']
higher_degree_branch_choices = ["H101", "H103", "H112", "H123", "H129", "H140", "H141", "H106", "H151", "H152"]
hostel_choices = ['AH1', 'AH2', 'AH3', 'AH4', 'AH5', 'AH6', 'AH7', 'AH8', 'AH9',
                  'CH1', 'CH2', 'CH3', 'CH4', 'CH5', 'CH6', 'CH7',
                  'DH1', 'DH2', 'DH3', 'DH4', 'DH5', 'DH6']
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

# username for the below functions will be of the format `[pf]\d{8}`

def fake_bitsID(username):
    year = username[1:5]
    uid = username[5:]
    branch = str(random.choice(branch_choices))
    return f"{year}{branch}PS{uid}G"


def fake_phd(username):
    year = username[1:5]
    uid = username[5:]
    branch = 'PHX' + str(random.choice(['P', 'F']))
    return str(year + branch + uid + 'G')


def fake_higher_degree(username):
    year = username[1:5]
    uid = username[5:]
    branch = str(random.choice(higher_degree_branch_choices))
    return f"{year}{branch}{uid}G"

def create_super_user():
    try:
        (super_user, created) = User.objects.get_or_create(username="admin", is_superuser=True)
        super_user.set_password('password')
        super_user.is_staff = True
        super_user.is_admin = True
        super_user.is_superuser = True
        super_user.save()
    except:
        print("Error occurred while creating superuser.")

def create_students_list(PER_BATCH_SIZE, YEAR_START, YEAR_END):
    """Creates a list of Users, then maps a Student to each User"""

    # First, generate the list of student users
    mUser_list = [None]*(PER_BATCH_SIZE * (YEAR_END - YEAR_START + 1))
    function_prefix_list = []
    stime = time.time()
    print("Creating Student Users...", end=" ")
    counter = 0
    for year in range(YEAR_START, YEAR_END+1):
        for id in range(PER_BATCH_SIZE):
            i = year*10000 + id*10000//PER_BATCH_SIZE
            [fake_id_function, prefix] = [[fake_phd, 'p'], [fake_bitsID, 'f'], [fake_higher_degree, 'h']][random.randint(0, 2)]
            function_prefix_list.append([fake_id_function, prefix])
            mUser = User(
                username = f"{prefix}{i}",
                first_name = f"Student{i}",
                email = f"{prefix}{i}@goa.bits-pilani.ac.in"
            )
            mUser.set_password('password')
            mUser_list[counter] = mUser

            counter += 1
        
    # Save the list of users
    with transaction.atomic():
        User.objects.bulk_create(mUser_list)
    print(f"{len(mUser_list)} created in {time.time() - stime:.3f}s")

    mUser_list = User.objects.all()

    # Next, generate a list of students
    students_list = []
    stime = time.time()
    print("Creating Students...", end=" ")
    counter = 0
    for year in range(YEAR_START, YEAR_END+1):
        for id in range(PER_BATCH_SIZE):
            i = year*10000 + id*10000//PER_BATCH_SIZE
            mUser = mUser_list[counter]
            [fake_id_function, prefix] = function_prefix_list[counter]
            mStudent = Student(
                user=mUser,
                name=f'Student {i}',
                bitsId=fake_id_function(mUser.username),
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
            students_list.append(mStudent)

            counter += 1
    
    with transaction.atomic():
        Student.objects.bulk_create(students_list)
    print(f"{len(students_list)} created in {time.time() - stime:.3f}s")

def create_wardens():
    """Creates a list of Users, then maps a Warden to each User"""

    # First, generate the list of warden users
    user_list = []
    stime = time.time()
    print("Creating Warden Users...", end=" ")
    for i in range(len(hostel_choices)):
        user = User(
            username='warden' + str(i),
            first_name='Warden' + str(i),
            email=f"warden{i}@goa.bits-pilani.ac.in"
        )
        user.set_password('password')
        user_list.append(user)

    # Save the list of users
    with transaction.atomic():
        User.objects.bulk_create(user_list)
    print(f"{len(user_list)} created in {time.time() - stime:.3f}s")

    user_list = User.objects.all()
    user_list = user_list[len(user_list) - len(hostel_choices):]

    # Next, generate a list of wardens
    warden_list = []
    stime = time.time()
    print("Creating Wardens...", end=" ")
    for i in range(len(hostel_choices)):
        user = user_list[i]
        warden = Warden(
            user=user,
            name='Warden' + str(i),
            chamber='BX12',
            residence='D111',
            phone_off=fake_number_generator(),
            phone_res=fake_number_generator(),
            email=user.email,
            hostel=hostel_choices[i],
        )
        warden_list.append(warden)
    
    with transaction.atomic():
        Warden.objects.bulk_create(warden_list)
    print(f"{len(warden_list)} created in {time.time() - stime:.3f}s")

def create_hostel_allotments(student_list):
    hostel_allotments_list = []

    stime = time.time()
    print("Creating HostelPS...", end=" ")

    for i, student in enumerate(student_list):
        status = fake_status()
        hostel = ''
        room = ''
        ps_station = ''
        acadstudent= False
        if status == 'Student':
            hostel = fake_hostel()
            room = fake_number_generator(3,1)
            acadstudent = True
        elif status == 'Thesis':
            ps_station = 'thesis station here'
        elif status == 'PS2':
            ps_station = 'ps station here'
        elif status == 'Graduate':
            hostel = 'Graduate'

        hostel_allotment = HostelPS(
            student=student,
            acadstudent=acadstudent,
            status=status,
            psStation=ps_station,
            hostel=hostel,
            room=room,
        )
        hostel_allotments_list.append(hostel_allotment)
    
    with transaction.atomic():
        HostelPS.objects.bulk_create(hostel_allotments_list)
    
    print(f"{len(hostel_allotments_list)} created in {time.time() - stime:.3f}s")

def create_mess_allotments(student_list):
    mess_allotment_list = []

    stime = time.time()
    print("Creating Mess Allotments...", end=" ")

    for student in student_list:
        mess_allotment = MessOption(
            student=student,
            monthYear=timezone.now().date(),
            mess=fake_mess()
        )
        mess_allotment_list.append(mess_allotment)
    
    with transaction.atomic():
        MessOption.objects.bulk_create(mess_allotment_list)
    
    print(f"{len(mess_allotment_list)} created in {time.time() - stime:.3f}s")

def create_bonafides(student_list):
    bonafides_list = []

    stime = time.time()
    print("Creating Bonafides...", end=" ")

    for student in student_list:
        bonafide = Bonafide(
            student=student,
            reason=fake_bonafide(),
            reqDate=timezone.now(),
        )
        bonafides_list.append(bonafide)
    
    with transaction.atomic():
        Bonafide.objects.bulk_create(bonafides_list)
    
    print(f"{len(bonafides_list)} created in {time.time() - stime:.3f}s")

def create_leaves(student_list):
    leave_list = []

    stime = time.time()
    print("Creating Leaves...", end=" ")

    for student in student_list:
        hostel = HostelPS.objects.get(student = student)
        if hostel.hostel in hostel_choices:
            warden = Warden.objects.get(hostel = hostel.hostel)
                
            status = fake_boolean()
            leave = Leave(
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
            leave_list.append(leave)
    
    with transaction.atomic():
        Leave.objects.bulk_create(leave_list)
    
    print(f"{len(leave_list)} created in {time.time() - stime:.3f}s")

def create_csas(student_list):
    csa_list = []

    stime = time.time()
    print("Creating CSAs...", end=" ")

    for i in range(5):
        # Inaccurate: Instead of making the CSAs out of the first 5 students, choose the first 5 non PHD non HD instead
        csa = CSA(
            student=student_list[i],
            title='President',
            email='prez@goa.bits-pilani.ac.in',
            pic = '2017A4PS0590_bsKDJSY.jpg',
            priority = i + 1
        )
        csa_list.append(csa)
    
    with transaction.atomic():
        CSA.objects.bulk_create(csa_list)
    
    print(f"{len(csa_list)} created in {time.time() - stime:.3f}s")

def create_securities(number=10):
    """Creates a list of Users, then maps a Security to each User"""

    # First, generate the list of security users
    user_list = []
    stime = time.time()
    print("Creating Security Users...", end=" ")
    for i in range(number):
        user = User(
            username=f'security{i}',
            first_name=f'security{i}',
            email=f"security{i}@goa.bits-pilani.ac.in"
        )
        user.set_password('password')
        user_list.append(user)
        
    # Save the list of users
    with transaction.atomic():
        User.objects.bulk_create(user_list)
    print(f"{len(user_list)} created in {time.time() - stime:.3f}s")

    user_list = User.objects.all()
    user_list = user_list[len(user_list) - number:]

    # Next, generate a list of securities
    security_list = []
    stime = time.time()
    print("Creating Securities...", end=" ")
    for i in range(number):
        user = user_list[i]
        security = Security(
            user=user
        )
        security_list.append(security)
    
    with transaction.atomic():
        Security.objects.bulk_create(security_list)
    print(f"{len(security_list)} created in {time.time() - stime:.3f}s")

def create_hostelsuperintendents():
    """Creates a list of Users, then maps a HostelSuperIntendent to each User"""

    # One Superintendent can be in charge of multiple hostels, so we need a nice way to generate some permutations
    # But I'm not smart enough for that right now, so I'll just make one superintendent in charge of two consecutive hostels
    combinations = [hostel_choices[i:i+2] for i in range(len(hostel_choices)-1)]
    superintendent_jurisdictions = [", ".join(combination) for combination in combinations]

    # First, generate the list of superintendent users
    user_list = []
    stime = time.time()
    print("Creating Superintendent Users...", end=" ")
    for i in range(len(superintendent_jurisdictions)):
        user = User(
            username='superintendent' + str(i),
            first_name='superintendent' + str(i),
            email='superintendent' + str(i) +"@goa.bits-pilani.ac.in"
        )
        user.set_password('password')
        user_list.append(user)
        
    # Save the list of users
    with transaction.atomic():
        User.objects.bulk_create(user_list)
    print(f"{len(user_list)} created in {time.time() - stime:.3f}s")

    user_list = User.objects.all()
    user_list = user_list[len(user_list) - len(superintendent_jurisdictions):]

    # Next, generate a list of superintendents
    superintendent_list = []
    stime = time.time()
    print("Creating Superintendents...", end=" ")
    for i in range(len(superintendent_jurisdictions)):
        user = user_list[i]
        superintendent = HostelSuperintendent(
            user=user,
            name=user.first_name,
            email=user.email,
            hostel=superintendent_jurisdictions[i],
            chamber='BX12',
            phone_off=fake_number_generator(),
            phone_res=fake_number_generator(),
            
        )
        superintendent_list.append(superintendent)
    
    with transaction.atomic():
        HostelSuperintendent.objects.bulk_create(superintendent_list)
    print(f"{len(superintendent_list)} created in {time.time() - stime:.3f}s")

def create_notices(number=15):
    notices = []
    for i in range(number):
        notice = Notice(date=datetime.datetime.now(), title=f"Notice {i+1}", desc="Notice description goes here")
        notices.append(notice)
    
    with transaction.atomic():
        Notice.objects.bulk_create(notices)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--per_batch_size', type=int, default=50, help='Student ID Range Start')
    parser.add_argument('--year_start', type=int, default=2016, help='The first batch year')
    parser.add_argument('--year_end', type=int, default=2021, help='The last batch year')
    parser.add_argument('--dataset_size', type=str, default="", help='The size of the generated dataset: large / medium / small\nOVERRIDES --per_batch_size')

    # Spread the arguments into constant local vars
    args = vars(parser.parse_args())
    PER_BATCH_SIZE = args["per_batch_size"]
    YEAR_START = args["year_start"]
    YEAR_END = args["year_end"]
    DATASET_SIZE = args["dataset_size"]
    
    # If DATASET_SIZE is given, convert PER_BATCH_SIZE accordingly
    DATASET_SIZES = {
        "large": 100,
        "medium": 50,
        "small": 15
    }
    if DATASET_SIZE != "" and DATASET_SIZE in DATASET_SIZES:
        PER_BATCH_SIZE = DATASET_SIZES[DATASET_SIZE]

    agreed = input("THIS WILL CLEAR ALL THE EXISTING DATABASE RECORDS. Continue? [Y/n]: ")
    if not agreed in  ['Y', 'y', 'YES']:
        print("Exited without editing")
        exit()

    print("Clearing existing database...", end=" ")
    stime = time.time()
    Leave.objects.all().delete()
    HostelPS.objects.all().delete()
    MessOption.objects.all().delete()
    Bonafide.objects.all().delete()
    Student.objects.all().delete()
    Warden.objects.all().delete()
    User.objects.all().delete()
    CSA.objects.all().delete()
    Security.objects.all().delete()
    HostelSuperintendent.objects.all().delete()
    Notice.objects.all().delete()
    print(f"cleared in {time.time() - stime:.3f}s")

    stime = time.time()

    create_students_list(PER_BATCH_SIZE, YEAR_START, YEAR_END)

    students_list = Student.objects.all()

    create_wardens()
    create_hostel_allotments(students_list)
    create_mess_allotments(students_list)
    create_bonafides(students_list)
    create_leaves(students_list)
    create_csas(students_list)
    create_securities(number=10)
    create_hostelsuperintendents()
    create_notices(number=15)

    create_super_user()

    print(f"\nDataset completed in {time.time() - stime:.3f}s")