import requests
from main.models import Student
from django.core.files import File
from pathlib import Path
from django.http import HttpResponse
import os

def insert(requests):
    ctr = 0
    failed_ids = []
    f = ""
    if os.path.isdir("ProfilePictures"):
        for i in os.listdir("ProfilePictures"):
            for j in os.listdir("ProfilePictures/" + i):
                try:
                    student = Student.objects.get(bitsId=j[:13])
                    student.profile_picture.save(j, File(open('ProfilePictures/' + i + '/' + j, 'rb')))
                    ctr= ctr+1
                except Exception as e:
                    pass
        return HttpResponse("Number of images added = " + str(ctr))
    else:
        return HttpResponse("No such directory named ProfilePictures found.")