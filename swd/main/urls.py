from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView


from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    # Django Login
    url(r'^login/', views.loginform, name="login"),
    url(r'^logout/', views.logoutform, name="logout"),

    #login_success
    url(r'^accounts/profile/', views.login_success, name='login-success'),


    url(r'^dashboard/', views.dashboard, name="dashboard"),
    url(r'^profile/', views.profile, name="profile"),
    url(r'^messoption/', views.messoption, name="messoption"),
    url(r'^leave/', views.leave, name="leave"),
    url(r'^certificates/', views.certificates, name="certificates"),
    url(r'bonafide/(?P<id>\d+)/$',views.printBonafide, name="printBonafide"),
    url(r'^warden/$', views.warden, name="warden"),
    url(r'^hostelsuperintendent/$', views.hostelsuperintendent, name="hostelsuperintendent"),
    url(r'^warden/([0-9]+)/$', views.wardenleaveapprove, name="wardenleaveapprove"),
    url(r'^hostelsuperintendent/([0-9]+)/$', views.hostelsuperintendentdaypassapprove, name="hostelsuperintendentdaypassapprove"),
    url(r'^daypass/', views.daypass, name="daypass"),
    # url(r'^studentimg/', views.studentimg, name="studentimg"),
    url(r'^store/', views.store, name="store"),
    url(r'^dues/', views.dues, name="dues"),
    url(r'^documents/', views.documents, name="documents"),
    url(r'^search/', views.search, name="search"),
    url(r'^student/(?P<id>\d+)/$',views.studentDetails, name="studentDetails"),
    url(r'^messbill/', views.messbill, name='messbill'),
    url(r'^import_mess_bill/', views.import_mess_bill, name='import_mess_bill'),
    url(r'^notice/',views.notice, name='notice'),
    url(r'^antiragging/',views.antiragging, name='antiragging'),
    url(r'^swd/',views.swd, name='swd'),
    url(r'^csa/',views.csa, name='csa'),
    url(r'^sac/',views.sac, name='sac'),
    url(r'^latecomer/', views.latecomer, name="latecomer"),
    url(r'^contact/',views.contact, name='contact'),
    url(r'^dash_security/',views.dash_security, name='dash_security'),
    url(r'^developers/', views.developers, name="developers"),
    url(r'^mess-forgot/',views.mess_import, name='forgot'),
    url(r'^mess_exp/',views.mess_exp, name='mess_exp'),
    #url(r'^mess_filter/',views.mess_filter, name='mess_filter'),
    url(r'^dues_dashboard/', views.dues_dashboard, name='dues_dashboard'),
    url(r'^import_dues_from_sheet/', views.import_dues_from_sheet, name='import_dues_from_sheet'),
    url(r'^publish_dues/', views.publish_dues, name='publish_dues'),
    url(r'^admin/edit_constants/', views.edit_constants, name='edit_constants'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
