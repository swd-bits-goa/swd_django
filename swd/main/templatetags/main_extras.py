from django import template

from main.models import Warden, HostelSuperintendent, Security

register = template.Library()

@register.simple_tag
def active_page(request, view_name):
    from django.urls import resolve, Resolver404
    path = resolve(request.path_info)
    if not request:
        return ""
    try:
        return "active" if path.url_name == view_name else ""
    except Resolver404:
        return ""


def is_warden(user):
    return False if not Warden.objects.filter(user=user) else True

def is_hostelsuperintendent(user):
     return False if not HostelSuperintendent.objects.filter(user=user) else True

def is_security(user):
    return False if not Security.objects.filter(user=user) else True


@register.simple_tag
def get_user_status(request):
    if request.user.is_authenticated:
        if is_warden(request.user):
            return 'warden'
        elif is_security(request.user):
            return 'security'
        elif is_hostelsuperintendent(request.user):
            return 'hostelsuperintendent'
        elif request.user.is_staff:
            return 'staff'
        else:
            return 'authenticated'
    else:
        return 'unauthenticated'


def get_base_template(request):
    userstatus = get_user_status(request)
    if userstatus == 'warden':
        return 'wardenbase.html'
    elif userstatus == 'security':
        return 'security_dash_base.html'
    elif userstatus == 'hostelsuperintendent':
        return 'superintendentbase.html'
    else:
        return 'indexbase.html'