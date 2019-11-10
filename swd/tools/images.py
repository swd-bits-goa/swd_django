import requests
from main.models import Student
from django.core.files import File
from pathlib import Path
from django.http import HttpResponse
import os

def insert(requests):
    ctr = 0
    if os.path.isdir("ProfilePictures"):
        for i in os.listdir("ProfilePictures"):
            try:
                student = Student.objects.get(bitsId=i[:13])
                student.profile_picture.save(i , File(open('ProfilePictures/' + i, 'rb')))
                ctr= ctr+1
            except Exception as e:
                print(e)
                print('fail')
        return HttpResponse("Number of images added = " + str(ctr))
    else:
        return HttpResponse("No such directory named ProfilePictures found.")