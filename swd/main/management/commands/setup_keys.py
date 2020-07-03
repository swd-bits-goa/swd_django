from django.core.management.base import BaseCommand, CommandError
from django.core.management.utils import get_random_secret_key
import random
import os

class Command(BaseCommand):
    help = 'Creates SALT and SECRET KEY for site development.'

    def handle(self, *args, **options):
        EMAIL_HOST_PASSWORD = 'myemailpassword'
        SALT_IMG = str(random.randint(10e+10, 10e+11-1))
        SECRET_KEY = str(get_random_secret_key())

        addr = os.getcwd()
        addr = os.path.join(addr, 'tools', 'dev_info.py')
        with open(addr, 'w') as devfile:
            devfile.write("EMAIL_HOST_PASSWORD = '" + EMAIL_HOST_PASSWORD + "'\n")
            devfile.write("SALT_IMG = '" + SALT_IMG + "'\n")
            devfile.write("SECRET_KEY = '" + SECRET_KEY + "'\n")

        self.stdout.write(self.style.SUCCESS("Successfully created dev_info.py"))
