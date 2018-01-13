from django.contrib.auth.models import User
from urllib.request import urlopen
from urllib.parse import urlencode

class LDAPAuthBackend:
    def authenticate(self, username=None, password=None):
        try:
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
