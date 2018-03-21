import graphene
from graphene_django.types import DjangoObjectType
from django.contrib.auth.models import User
from .models import *
from datetime import datetime


class UserType(DjangoObjectType):
    class Meta:
        model = User

class WardenType(DjangoObjectType):
    class Meta:
        model = Warden

class StaffType(DjangoObjectType):
    class Meta:
        model = Staff

class StudentType(DjangoObjectType):
    class Meta:
        model = Student

class DayScholarType(DjangoObjectType):
    class Meta:
        model = DayScholar

class HostelPSType(DjangoObjectType):
    class Meta:
        model = HostelPS

class CSAType(DjangoObjectType):
    class Meta:
        model = CSA

class MessOptionType(DjangoObjectType):
    class Meta:
        model = MessOption

class BonafideType(DjangoObjectType):
    class Meta:
        model = Bonafide

class LeaveType(DjangoObjectType):
    class Meta:
        model = Leave

class DayPassType(DjangoObjectType):
    class Meta:
        model = DayPass

class LateComerType(DjangoObjectType):
    class Meta:
        model = LateComer

class InOutType(DjangoObjectType):
    class Meta:
        model = InOut

class DiscoType(DjangoObjectType):
    class Meta:
        model = Disco

class MessOptionOpenType(DjangoObjectType):
    class Meta:
        model = MessOptionOpen

class TransactionType(DjangoObjectType):
    class Meta:
        model = Transaction

class MessBillType(DjangoObjectType):
    class Meta:
        model = MessBill


class Query(object):
    # used to get all data to the frontend
    current_user = graphene.Field(UserType)


    all_users = graphene.List(UserType)
    user = graphene.Field(
        UserType,
        id=graphene.Int(),
        username = graphene.String()
    )

    all_wardens = graphene.List(WardenType)
    warden = graphene.Field(
        WardenType,
        id=graphene.Int(),
        username = graphene.String()
    )

    all_staffs = graphene.List(StaffType)
    staff = graphene.Field(
        StaffType,
        id=graphene.Int(),
        username = graphene.String()
    )

    all_students = graphene.List(StudentType)
    student = graphene.Field(
        StudentType,
        id=graphene.Int(),
        username = graphene.String(),
        name = graphene.String(),
        bitsId = graphene.String()
    )
    search_student = graphene.Field(
        graphene.List(StudentType),
        search=graphene.String(),
        hostel=graphene.List(graphene.String),
        branch=graphene.List(graphene.String)
    )

    all_day_scholars = graphene.List(DayScholarType)
    day_scholar = graphene.Field(
        DayScholarType,
        id=graphene.Int(),
        username = graphene.String()
    )

    hostelps = graphene.Field(
        HostelPSType,
        id=graphene.Int(),
        username = graphene.String()
    )

    all_csas = graphene.List(CSAType)
    csa = graphene.Field(
        CSAType,
        id=graphene.Int(),
        username = graphene.String()
    )

    all_mess_options = graphene.List(MessOptionType)
    messoption = graphene.Field(
        MessOptionType,
        id=graphene.Int(),
        username = graphene.String()
    )

    all_bonafides = graphene.List(BonafideType)
    bonafide = graphene.Field(
        BonafideType,
        id=graphene.Int(),
        username = graphene.String()
    )

    all_leaves = graphene.List(LeaveType)
    leave = graphene.Field(
        LeaveType,
        id=graphene.Int(),
        username = graphene.String()
    )

    all_day_passs = graphene.List(DayPassType)
    daypass = graphene.Field(
        DayPassType,
        id=graphene.Int(),
        username = graphene.String()
    )

    all_late_comers = graphene.List(LateComerType)
    latecomer = graphene.Field(
        LateComerType,
        id=graphene.Int(),
        username = graphene.String()
    )

    all_in_outs = graphene.List(InOutType)
    inout = graphene.Field(
        InOutType,
        id=graphene.Int(),
        username = graphene.String()
    )

    all_discos = graphene.List(DiscoType)
    disco = graphene.Field(
        DiscoType,
        id=graphene.Int(),
        username = graphene.String()
    )

    all_mess_option_opens = graphene.List(MessOptionOpenType)
    messoptionopen = graphene.Field(
        MessOptionOpenType,
        id=graphene.Int(),
        username = graphene.String()
    )

    all_transactions = graphene.List(TransactionType)
    transaction = graphene.Field(
        TransactionType,
        id=graphene.Int(),
        username = graphene.String()
    )

    all_mess_bills = graphene.List(MessBillType)
    messbill = graphene.Field(
        MessBillType,
        id=graphene.Int(),
        username = graphene.String()
    )

    def resolve_current_user(self, args, **kwargs):
        context = args.context
        if not context.user.is_authenticated:
            return None
        else:
            return args.context.user

    def resolve_all_users(self, args, **kwargs):
        return User.objects.all()

    def resolve_user(self, args, **kwargs):
        id = kwargs.get('id')
        username = kwargs.get('username')

        if id is not None:
           return User.objects.get(id=id)

        if username is not None:
            return User.objects.get(username=username)

        return None

    def resolve_all_wardens(self, args, **kwargs):
        return Warden.objects.all()

    def resolve_warden(self, args, **kwargs):
        id = kwargs.get('id')
        username = kwargs.get('username')

        if id is not None:
           return Warden.objects.get(id=id)

        if username is not None:
            user = User.objects.get(username=username)
            return Warden.objects.get(user=user)

        return None

    def resolve_all_staffs(self, args, **kwargs):
        return Staff.objects.all()

    def resolve_staff(self, args, **kwargs):
        id = kwargs.get('id')
        username = kwargs.get('username')

        if id is not None:
           return Staff.objects.get(id=id)

        if username is not None:
            user = User.objects.get(username=username)
            return Staff.objects.get(user=user)

        return None


    def resolve_all_students(self, args, **kwargs):
        return Student.objects.all()

    def resolve_student(self, args, **kwargs):
        id = kwargs.get('id')
        username = kwargs.get('username')
        name = kwargs.get('name')
        bitsId = kwargs.get('bitsId')


        if id is not None:
           return Student.objects.get(id=id)

        if username is not None:
            user = User.objects.get(username=username)
            return Student.objects.get(user=user)

        return None

    def resolve_search_student(self, args, **kwargs):
        search = kwargs.get('search')
        hostel = kwargs.get('hostel')
        branch = kwargs.get('branch')
        searchresults = []
        flag=0
        if hostel:
            hostels=[]
            for host in hostel:
                hostels.extend(HostelPS.objects.all().filter(hostel=host))
            for hostel in hostels:
                searchresults.append(hostel.student)
            if len(searchresults)==0:
                flag=1
        if branch:
            if len(searchresults):
                students = searchresults
                searchresults = []
            else:
                students = Student.objects.all()
            for student in students:
                for bran in branch:
                    if student.bitsId[4:6]==bran:
                        searchresults.append(student)
            if len(searchresults)==0:
                flag=1
        if search:
            if search[0].isalpha():
                if len(searchresults):
                    students = searchresults
                    searchresults = []
                elif flag==0:
                    students = Student.objects.all().filter(name__icontains=search)
                else:
                    students=[]
                for student in students:
                    names = student.name.split()
                    for name in names:
                        if name.startswith(search.upper()):
                            searchresults.append(student)
                    if(len(searchresults)>9):
                        break
            elif search[0].isdigit():
                if len(search)>2:
                    if len(searchresults):
                        students = searchresults
                        searchresults = []
                    elif flag==0:
                        students = Student.objects.all().filter(bitsId__icontains=search)
                    else:
                        students=[]
                    for student in students:
                        if student.bitsId.startswith(search.upper()):
                            searchresults.append(student)
                else:
                    searchresults = searchresults
        return searchresults

    def resolve_all_day_scholars(self, args, **kwargs):
        return DayScholar.objects.all()

    def resolve_dayscholar(self, args, **kwargs):
        id = kwargs.get('id')
        username = kwargs.get('username')

        if id is not None:
           return DayScholar.objects.get(id=id)

        if username is not None:
            user = User.objects.get(username=username)
            student = Student.objects.get(user=user)
            return DayScholar.objects.get(student=student)

        return None
###

    def resolve_hostelps(self, args, **kwargs):
        id = kwargs.get('id')
        username = kwargs.get('username')

        if id is not None:
           return HostelPS.objects.get(id=id)

        if username is not None:
            user = User.objects.get(username=username)
            student = Student.objects.get(user=user)
            return HostelPS.objects.get(student=student)

        return None

    def resolve_all_csas(self, args, **kwargs):
        return CSA.objects.all()

    def resolve_csa(self, args, **kwargs):
        id = kwargs.get('id')
        username = kwargs.get('username')

        if id is not None:
           return CSA.objects.get(id=id)

        if username is not None:
            user = User.objects.get(username=username)
            student = Student.objects.get(user=user)
            return CSA.objects.get(student=student)

        return None

    def resolve_all_mess_options(self, args, **kwargs):
        return MessOption.objects.all()

    def resolve_messoption(self, args, **kwargs):
        id = kwargs.get('id')
        username = kwargs.get('username')

        if id is not None:
           return MessOption.objects.get(id=id)

        if username is not None:
            user = User.objects.get(username=username)
            student = Student.objects.get(user=user)
            messoption = MessOption.objects.filter(student=student).latest('monthYear')
            if messoption and datetime.today().date() < MessOptionOpen.objects.latest('dateClose').dateClose:
                return messoption

        return None

    def resolve_all_bonafides(self, args, **kwargs):
        return Bonafide.objects.all()

    def resolve_bonafide(self, args, **kwargs):
        id = kwargs.get('id')
        username = kwargs.get('username')

        if id is not None:
           return Bonafide.objects.get(id=id)

        if username is not None:
            user = User.objects.get(username=username)
            student = Student.objects.get(user=user)
            return Bonafide.objects.filter(student=student)

        return None

    def resolve_all_leaves(self, args, **kwargs):
        return DayScholar.objects.all()

    def resolve_leave(self, args, **kwargs):
        id = kwargs.get('id')
        username = kwargs.get('username')

        if id is not None:
           return Leave.objects.get(id=id)

        if username is not None:
            user = User.objects.get(username=username)
            student = Student.objects.get(user=user)
            return Leave.objects.filter(student=student)

        return None

    def resolve_all_day_passs(self, args, **kwargs):
        return DayPass.objects.all()

    def resolve_daypass(self, args, **kwargs):
        id = kwargs.get('id')
        username = kwargs.get('username')

        if id is not None:
           return DayPass.objects.get(id=id)

        if username is not None:
            user = User.objects.get(username=username)
            student = Student.objects.get(user=user)
            return DayPass.objects.filter(student=student)

        return None

    def resolve_all_late_comers(self, args, **kwargs):
        return LateComer.objects.all()

    def resolve_latecomer(self, args, **kwargs):
        id = kwargs.get('id')
        username = kwargs.get('username')

        if id is not None:
           return LateComer.objects.get(id=id)

        if username is not None:
            user = User.objects.get(username=username)
            student = Student.objects.get(user=user)
            return LateComer.objects.filter(student=student)

        return None

    def resolve_all_Discos(self, args, **kwargs):
        return Disco.objects.all()

    def resolve_disco(self, args, **kwargs):
        id = kwargs.get('id')
        username = kwargs.get('username')

        if id is not None:
           return Disco.objects.get(id=id)

        if username is not None:
            user = User.objects.get(username=username)
            student = Student.objects.get(user=user)
            return Disco.objects.filter(student=student)

        return None

    def resolve_all_mess_option_opens(self, args, **kwargs):
        return MessOptionOpen.objects.all()

    def resolve_messoptionopen(self, args, **kwargs):
        id = kwargs.get('id')
        username = kwargs.get('username')

        if id is not None:
           return MessOptionOpen.objects.get(id=id)

        if username is not None:
            user = User.objects.get(username=username)
            student = Student.objects.get(user=user)
            return MessOptionOpen.objects.filter(student=student)

        return None

    def resolve_all_transactions(self, args, **kwargs):
        return Transaction.objects.all()

    def resolve_transaction(self, args, **kwargs):
        id = kwargs.get('id')
        username = kwargs.get('username')

        if id is not None:
           return Transaction.objects.get(id=id)

        if username is not None:
            user = User.objects.get(username=username)
            student = Student.objects.get(user=user)
            return Transaction.objects.filter(student=student)

        return None

    def resolve_all_mess_bills(self, args, **kwargs):
        return MessBill.objects.all()

    def resolve_messbill(self, args, **kwargs):
        id = kwargs.get('id')
        username = kwargs.get('username')

        if id is not None:
           return MessBill.objects.get(id=id)

        if username is not None:
            user = User.objects.get(username=username)
            student = Student.objects.get(user=user)
            return MessBill.objects.filter(student=student)

        return None
