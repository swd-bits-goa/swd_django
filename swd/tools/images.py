from .dev_info import info
import shutil
import requests
from main.models import Student
from django.core.files import File
from pathlib import Path
from django.http import HttpResponse
'''
def index(request):
    for inf in info:
        bitsId = inf[0][:-1]
        if Path('../ProfilePictures/' + bitsId[:12] + '.jpg').is_file():
            print(bitsId + 'Exists')
        else:
            pass
            try:
                url = 'https://swd.bits-goa.ac.in/css/studentImg/' + bitsId[:12] + '.jpg'
                response = requests.get(url, stream=True, verify=False)
                with open('../ProfilePictures/' + bitsId[:12] + '.jpg', 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                    print(bitsId)
                del response
            except Exception as e:
                print(e)
                print('fail')
    return HttpResponse("Images downloaded")
'''
def insert(requests):
    for inf in info:
        print(inf[0][:-1])
        try:
            student = Student.objects.get(bitsId=inf[0])
            student.profile_picture.save(inf[0][:-1] + '.jpg', File(open('../ProfilePictures/' + inf[0][:-1] + '.jpg', 'rb')))
        except Exception as e:
            print(e)
            print('fail')
