from django.contrib.auth.models import User
from urllib.request import urlopen
from urllib.parse import urlencode
from django.contrib.auth.backends import ModelBackend

class LDAPAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            print(username, password)
            with urlopen("http://10.10.10.20/auth.php?" + urlencode({'u': username, 'p': password}), timeout=5) as authfile:
                string = authfile.read()
                
                print(string)
                if string.decode('utf-8') == 'true':
                    try:
                        u = User.objects.get(username__exact=username)
                        return u
                    except Exception as e:
                        print(e)
                        return None
        except Exception as e:
            print(e)
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
