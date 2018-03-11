from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse
from main.models import Student, HostelPS
from .dev_info import users

def index(request):
    for bitsId, name, hostel, room, username, day_scholar in users:
        print()
        print(bitsId, end='')
        active=True
        if username=='':
            username = bitsId[0:5] + '0' + bitsId[5:]
            active=False
        password = User.objects.make_random_password()
        email = username + '@goa.bits-pilani.ac.in'
        try:
            user = User.objects.create_user(username, email, password)
            if not active:
                user.is_active = False
            user.save()
        except:
            print("(Fail Username)")
        
        try:
            user = User.objects.get(username = username)
            profile = Student.objects.create(user=user, name=name, bitsId=bitsId)
            profile.save()
        except Exception as e:
            print('Fail (Profile)')
            print(e)

        try:
            user = User.objects.get(username = username)
            student = Student.objects.get(user=user)
            if hostel == 'Graduate' or hostel == 'Thesis' or hostel == 'PS2' or hostel == '':
                acadstudent = False
                status = 'Graduate' if hostel == '' else hostel
                psStation = room
                hostel = ''
                room = ''
            else:
                acadstudent = True
                status = 'Student'
                psStation = ''
            
            hostelps = HostelPS.objects.create(student=student, acadstudent=acadstudent, status=status, psStation=psStation, hostel=hostel, room=room)
            hostelps.save()
        except Exception as e:
            print('Fail (Hostel)')
            print(e)

    return HttpResponse("Done")
