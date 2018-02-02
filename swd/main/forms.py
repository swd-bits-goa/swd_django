from django import forms
from .models import MessOption, Leave, Bonafide, DayPass
from django.forms.widgets import TextInput, Textarea
from django.utils.translation import ugettext_lazy as _
from datetime import date, datetime

class MessForm(forms.ModelForm):
    class Meta:
        model = MessOption
        fields = ['mess']

class LeaveForm(forms.ModelForm):
    dateStart = forms.CharField(label='Departure Date', widget=forms.TextInput(attrs={'class': 'datepicker'}))
    timeStart = forms.CharField(label='Departure Time', widget=forms.TextInput(attrs={'class': 'timepicker'}))
    dateEnd = forms.CharField(label='Arrival Date', widget=forms.TextInput(attrs={'class': 'datepicker'}))
    timeEnd = forms.CharField(label='Arrival Time', widget=forms.TextInput(attrs={'class': 'timepicker'}))
    
    def clean(self):
        cleaned_data = super(LeaveForm, self).clean()
        dateStart = datetime.strptime(cleaned_data['dateStart'], '%d %B, %Y').date()
        dateEnd = datetime.strptime(cleaned_data['dateEnd'], '%d %B, %Y').date()
        if (dateStart > dateEnd):
            self.add_error('dateEnd', "Arrival cannot be before Departure!")
        if (dateStart < date.today()):
            self.add_error('dateStart', "Departure cannot be before today!")

    class Meta:
        model = Leave
        exclude = ['dateTimeStart', 'dateTimeEnd', 'student',
                   'approvedBy', 'approved', 'disapproved', 'inprocess', 'comment']
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

        labels = {
            'otherReason': _('Please mention if other reason'),
        }

class printBonafideForm(forms.Form):
    text = forms.CharField(required=True, label='Body Text', widget=forms.Textarea(attrs={'class': 'materialize-textarea'}))

class DayPassForm(forms.ModelForm):
    date = forms.CharField(label='Date', widget=forms.TextInput(attrs={'class': 'datepicker'}))
    time = forms.CharField(label='Time', widget=forms.TextInput(attrs={'class': 'timepicker'}))

    def clean(self):
        cleaned_data = super(DayPassForm, self).clean()
        date = datetime.strptime(cleaned_data['date'], '%d %B, %Y').date()
        if (date < date.today()):
            self.add_error('date', "Daypass cannot be issued for dates before today!")
        return cleaned_data

    class Meta:
        model = DayPass
        exclude = ['student', 'approvedBy',
                    'approved', 'comment', 'disapproved', 'inprocess', 'dateTime']
        widgets = {
            'reason': forms.Textarea(attrs={'class': 'materialize-textarea'}),
        }
        labels = {
            'consent': _('Parent Consent Type'),
        }
