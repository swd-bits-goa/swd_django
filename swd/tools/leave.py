from .dev_info import leaves

def index(request):
    from django.contrib.auth.models import User
    from main.models import Warden, Leave, Student
    from django.http import HttpResponse
    import datetime
    from django.utils.timezone import make_aware
    hostels = ['ah1', 'ah2', 'ah3', 'ah4', 'ah5', 'ah6', 'ah7', 'ah8', 'ah9', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7',]
    #Create hostel wardens
    for i in hostels:
        try:
            username = i + 'warden'
            email = username + '@goa.bits-pilani.ac.in'
            password = User.objects.make_random_password()
            user = User.objects.create_user(username, email, password)
            user.save()
        except Exception as e:
            print(e)

        try:
            username = i + 'warden'
            email = username + '@goa.bits-pilani.ac.in'
            user = User.objects.get(username=username)
            warden = Warden.objects.create(user=user,name=username,chamber='B111',residence='L101',phone='7777777777',email=email,hostel=i.upper())
        except Exception as e:
            print(e)
   
    for leaveid, loginID, studentID, sdate, stime, edate, etime, reason, approved_by, warden_approv, hostel, addr, ph, print_, dayscount, comment, consent in leaves:
        try:
            if len(loginID) == 8:
                loginID = loginID[:5] + '0' + loginID[5:]
            student = Student.objects.get(user__username=loginID)
            rev_sdate = datetime.datetime.strptime(sdate, '%d/%m/%Y')
            try:
                rev_stime = datetime.datetime.strptime(stime, '%H:%M').time()
            except:
                rev_stime = datetime.datetime.strptime(stime, '%I:%M:%S %p').time()
            print(rev_stime)
            sdatetime = datetime.datetime.combine(rev_sdate, rev_stime)
            rev_edate= datetime.datetime.strptime(edate, '%d/%m/%Y')
            try:
                rev_etime = datetime.datetime.strptime(etime, '%H:%M').time()
            except:
                rev_etime = datetime.datetime.strptime(etime, '%I:%M:%S %p').time()
            edatetime = datetime.datetime.combine(rev_edate, rev_etime)
            print(approved_by)
            try:
                warden = Warden.objects.get(user__username=approved_by)
            except:
                warden = Warden.objects.get(user__username='chiefwarden')
            if warden_approv == 'disapprov':
                approved=False
                inprocess=False
                disapproved=True
            elif warden_approv == 'YES':
                approved=True
                inprocess=False
                disapproved=False
            else:
                approved=False
                inprocess=True
                disapproved=False
            Leave.objects.create(student=student, dateTimeStart=make_aware(sdatetime), dateTimeEnd=make_aware(edatetime), reason=reason, consent=consent, corrAddress=addr, corrPhone=ph, approvedBy=warden, approved=approved, disapproved=disapproved, inprocess=inprocess, comment=comment)
        except Exception as e:
            print(loginID, e)
        
    return HttpResponse("Done")
