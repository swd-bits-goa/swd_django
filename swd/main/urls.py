from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView
from django.urls import path
from .views import verify_referral_id

from . import views
from .views import verify_student_id


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
    url(r'^vacation/$', views.vacation_no_mess, name="vacation_no_mess"),
    url(r'^certificates/', views.certificates, name="certificates"),
    url(r'bonafide/(?P<id>\d+)/$',views.printBonafide, name="printBonafide"),
    url(r'^warden/$', views.warden, name="warden"),
    url(r'^hostelsuperintendent/$', views.hostelsuperintendent, name="hostelsuperintendent"),
    url(r'^warden/([0-9]+)/$', views.wardenleaveapprove, name="wardenleaveapprove"),
    url(r'^hostelsuperintendent/([0-9]+)/$', views.hostelsuperintendentdaypassapprove, name="hostelsuperintendentdaypassapprove"),
    url(r'^daypass/', views.daypass, name="daypass"),
    url(r'^store/', views.store, name="store"),
    url(r'^order_form/(?P<bundle_id>[^/]+)/$', views.order_form, name="order_form"),

    url(r'^dues/', views.dues, name="dues"),
    url(r'^notices/', views.notices, name="notices"),
    url(r'^search/', views.search, name="search"),
    url(r'^student/(?P<id>\d+)/$',views.studentDetails, name="studentDetails"),
    url(r'^messbill/', views.messbill, name='messbill'),
    url(r'^import_mess_bill/', views.import_mess_bill, name='import_mess_bill'),
    url(r'^notice/',views.notice, name='notice'),
    url(r'^antiragging/',views.antiragging, name='antiragging'),
    url(r'^swd/',views.swd, name='swd'),
    url(r'^csa/',views.csa, name='csa'),
    url(r'^migration/',views.migration, name='migration'),
    url(r'^sac/',views.sac, name='sac'),
    url(r'^latecomer/', views.latecomer, name="latecomer"),
    url(r'^contact/',views.contact, name='contact'),
    url(r'^developers/', views.developers, name="developers"),
    url(r'^mess-forgot/',views.mess_import, name='forgot'),
    url(r'^mess_exp/',views.mess_exp, name='mess_exp'),
    url(r'^dues_dashboard/', views.dues_dashboard, name='dues_dashboard'),
    url(r'^import_dues_from_sheet/', views.import_dues_from_sheet, name='import_dues_from_sheet'),
    url(r'^publish_dues/', views.publish_dues, name='publish_dues'),
    url(r'^admin/edit_constants/', views.edit_constants, name='edit_constants'),
    url(r'^mess_leave_dashboard/', views.export_mess_leave, name="export_mess_leave"),

    url(r'address_dashboard/', views.address_approval_dashboard, name='address_approval_dashboard'),

    url(r'^admin/import_cgpa/', views.import_cgpa, name='import_cgpa'),

    url(r'^admin/add_new_students/', views.add_new_students, name='add_new_students'),
    url(r'^admin/add_new_wardens/', views.add_wardens, name='add_wardens'),
    url(r'^admin/add_new_superintendents/', views.add_superintendents, name='add_superintendents'),
    url(r'^admin/update_names/', views.update_names, name='update_names'),
    url(r'^admin/update_hostel/', views.update_hostel, name='add_hostels'),
    url(r'^admin/update_phone/', views.update_contact, name='add_phone'),
    url(r'^admin/update_parent_phone/', views.update_parent_contact, name='add_parentphone'),
    url(r'^admin/update_ids/', views.update_ids, name='update_ids'),
    url(r'^admin/update_ps/', views.update_ps, name='update_ps'),
    url(r'^admin/update_address/', views.update_address, name='update_address'),
    url(r'^admin/update_bank/', views.update_bank_account, name='update_bank'),
    url(r'^admin/update_parentemail/', views.update_parent_email, name='update_parentemail'),
    url(r'^admin/upload_latecomer/', views.upload_latecomer, name='update_latecomer'),
    url(r'^admin/upload_disco/', views.upload_disco, name='update_disco'),
    url(r'^admin/upload_profile_pictures', views.upload_profile_pictures, name="upload_profile_pictures"),
    url(r'^admin/upload_contact_pictures', views.upload_contact_pictures, name="upload_contact_pictures"),
    url(r'^leave_export/', views.leave_export, name='leave_export'),
    url(r'^leave_import/', views.leave_import, name='leave_import'),
    url(r'^hostel_export/', views.hostel_export, name='hostel_export'),
    url(r'^leave_diff/', views.leave_diff, name='leave_diff'),
    url(r'^admin/get_cor_add', views.get_corr_address, name='get_corr_address'),
    url(r'^admin/delete_students/',views.delete_students, name='delete_students'),
    url(r'^admin/view_duplicates/(?P<end_year>\d+)?/?', views.view_duplicates, name='view_duplicates'),

    path('verify-student-id/', verify_student_id, name='verify_student_id'),
    path('verify-referral-id/', verify_referral_id, name='verify_referral_id'),
    
    #API endpoints
    path('api/students-on-leave-today/', views.students_on_leave_today, name='students_on_leave_today'),




] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
