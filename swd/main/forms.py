from django import forms
from .models import MessOption, Leave, Bonafide, DayPass
from django.forms.widgets import TextInput, Textarea, FileInput
from django.utils.translation import ugettext_lazy as _
from datetime import date, datetime, timedelta


class MessForm(forms.ModelForm):
    class Meta:
        model = MessOption
        fields = ['mess']


class LeaveForm(forms.ModelForm):
    dateStart = forms.CharField(label='Departure Date', widget=forms.TextInput(attrs={'class': 'datepicker mask'}))
    timeStart = forms.CharField(label='Departure Time', widget=forms.TextInput(attrs={'class': 'timepicker mask'}))
    dateEnd = forms.CharField(label='Arrival Date', widget=forms.TextInput(attrs={'class': 'datepicker mask'}))
    timeEnd = forms.CharField(label='Arrival Time', widget=forms.TextInput(attrs={'class': 'timepicker mask'}))
    phone_number = forms.CharField(label='Contact No. during leave', widget=TextInput(attrs={'type':'number'}))

    def clean(self):
        cleaned_data = super(LeaveForm, self).clean()
        dateStart = datetime.strptime(cleaned_data['dateStart'], '%d %B, %Y').date()
        dateEnd = datetime.strptime(cleaned_data['dateEnd'], '%d %B, %Y').date()
        timeStart = datetime.strptime(cleaned_data['timeStart'], '%H:%M').time()
        date_time_start = datetime.combine(dateStart, timeStart)
        if (len(cleaned_data['phone_number']) != 10):
            self.add_error('phone_number', "Contact No. must have 10 digits")
        if (dateStart > dateEnd):
            self.add_error('dateEnd', "Arrival cannot be before Departure")
        if (datetime.now() >= date_time_start):
            self.add_error('dateStart', "Departure cannot be before the present date and time")
        if((date_time_start-datetime.now()).days>30):
            self.add_error('dateStart', "Can apply for leaves within a month only.")
        if (date_time_start - datetime.now()) <= timedelta(hours=12):
            self.add_error('dateStart', "Cannot apply for leave one day before departure. Contact warden for immediate leave approval")
        if (dateStart - dateEnd).days == 0:
            self.add_error('dateStart', "Start date and end date cannot be the same. Apply for a day pass instead")
        return cleaned_data

    class Meta:
        model = Leave
        exclude = ['dateTimeStart', 'dateTimeEnd', 'student',
                   'approvedBy', 'approved', 'disapproved', 'inprocess', 'comment', 'corrPhone']
        widgets = {
            'reason': forms.Textarea(attrs={'class': 'materialize-textarea validate'}),
            'corrAddress': forms.Textarea(attrs={'class': 'materialize-textarea validate'}),
        }
        labels = {
            'consent': _('Parent Consent Type'),
            'corrAddress': _('Address for Correspondence during Leave'),
            'corrPhone': _('Contact No. during Leave'),
        }


class BonafideForm(forms.ModelForm):
    class Meta:
        model = Bonafide
        fields = ['reason', 'otherReason']
        widgets = {
            'otherReason': forms.Textarea(attrs={'class': 'materialize-textarea'}),
            }
        labels = {
            'otherReason': _('Please mention if other reason'),
        }


class printBonafideForm(forms.Form):
    text = forms.CharField(required=True, label='Body Text', widget=forms.Textarea(attrs={'class': 'materialize-textarea'}))


class DayPassForm(forms.ModelForm):
    date = forms.CharField(label='Date', widget=forms.TextInput(attrs={'class': 'datepicker'}))
    time = forms.CharField(label='Out Time', widget=forms.TextInput(attrs={'class': 'timepicker'}))
    intime = forms.CharField(label='In Time', widget=forms.TextInput(attrs={'class': 'timepicker'}))
    document = forms.FileField(label="Any Supporting Document", required=False, widget=forms.FileInput(attrs={'class': 'file-field input-field'}))
    def clean(self):
        cleaned_data = super(DayPassForm, self).clean()
        date = datetime.strptime(cleaned_data['date'], '%d %B, %Y').date()
        time = datetime.strptime(cleaned_data['time'], '%H:%M').time()
        intime = datetime.strptime(cleaned_data['intime'], '%H:%M').time()
        date_time_start = datetime.combine(date, time)
        if datetime.now() >= date_time_start:
            self.add_error('date', "Daypass cannot be issued before the present date and time")
        if (date_time_start-datetime.now()).days>2:
            self.add_error('date', "Can apply for daypass within 2 days")
        if intime < time:
            self.add_error('intime', "In-time cannot be before out-time")
        return cleaned_data

    class Meta:
        model = DayPass
        exclude = ['student', 'approvedBy', 'approved', 'comment',
                   'disapproved', 'inprocess', 'dateTime','inTime']
        widgets = {
            'reason': forms.Textarea(attrs={'class': 'materialize-textarea'}),
            'corrAddress': forms.Textarea(attrs={'class': 'materialize-textarea validate'}),
            'document': forms.FileInput(attrs={'class': 'file-field input-field'}),
        }
        labels = {
            'corrAddress': _(" Location you're visiting "),
            'document': _("Any Supporting Document"),
        }


class VacationLeaveNoMessForm(forms.Form):
    out_date = forms.CharField(label='Out Date', widget=forms.TextInput(attrs={'class': 'datepicker'}))
    in_date = forms.CharField(label='In Date', widget=forms.TextInput(attrs={'class': 'datepicker'}))
    
    def clean(self):
        cleaned_data = super(VacationLeaveNoMessForm, self).clean()
        out_date = datetime.strptime(cleaned_data['out_date'], '%d %B, %Y').date()
        in_date = datetime.strptime(cleaned_data['in_date'], '%d %B, %Y').date()

        if out_date >= in_date:
            self.add_error(
                    'in_date',
                    "Vacation dates are inconsistent."
            )
        return cleaned_data

    class Meta:
        model = Leave
        exclude = ['dateTimeStart', 'dateTimeEnd', 'student',
                   'approvedBy', 'approved', 'disapproved',
                   'inprocess', 'comment', 'corrPhone',
                   'reason', 'corrAddress', 'consent', 'document']

