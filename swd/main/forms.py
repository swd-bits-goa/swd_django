from django import forms
from .models import MessOption, Leave, Bonafide, DayPass
from django.forms.widgets import TextInput, Textarea
from django.utils.translation import ugettext_lazy as _

class MessForm(forms.ModelForm):
    class Meta:
        model = MessOption
        fields = ['mess']

class LeaveForm(forms.ModelForm):
    dateStart = forms.CharField(label='Departure Date', widget=forms.TextInput(attrs={'class': 'datepicker'}))
    timeStart = forms.CharField(label='Departure Time', widget=forms.TextInput(attrs={'class': 'timepicker'}))
    dateEnd = forms.CharField(label='Arrival Date', widget=forms.TextInput(attrs={'class': 'datepicker'}))
    timeEnd = forms.CharField(label='Arrival Time', widget=forms.TextInput(attrs={'class': 'timepicker'}))

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
    class Meta:
        model = DayPass
        exclude = ['student', 'approvedBy',
                    'approved', 'comment']
        widgets = {
            'reason': forms.Textarea(attrs={'class': 'materialize-textarea'}),
        }
        labels = {
            'consent': _('Parent Consent Type'),
        }
