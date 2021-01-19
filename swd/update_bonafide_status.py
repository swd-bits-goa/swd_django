import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "swd.settings")
django.setup()

from main.models import Bonafide

bonafides = Bonafide.objects.all()

for bonafide in bonafides:
    if(bonafide.printed==True):
        bonafide.status = 'Approved'
    bonafide.save()
    print(bonafide.student, bonafide.printed, bonafide.status)
