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
                    id = j.split(".")[0]
                    id = id.upper()
                    student = Student.objects.get(bitsId=id)
                    student.profile_picture.save(j, File(open('ProfilePictures/' + i + '/' + j, 'rb')))
                    ctr= ctr+1
                    #f = f + id + "  "
                except Exception as e:
                    pass
                    #ctr = ctr + 1
                    #f=f+e
                    #break
        return HttpResponse("Number of images added = " + str(ctr))
        #return HttpResponse("Error  " + f) 
    else:
        return HttpResponse("No such directory named ProfilePictures found.")
