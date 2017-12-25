from django import forms
from .models import MessOption, Leave
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
                   'approvedBy', 'approved', 'comment']
        widgets = {
            'reason': forms.Textarea(attrs={'class': 'materialize-textarea'}),
            'corrAddress': forms.Textarea(attrs={'class': 'materialize-textarea'}),
        }
        labels = {
            'consent': _('Parent Consent Type'),
            'corrAddress': _('Address for Correspondence during Leave'),
            'corrPhone': _('Contact No. during Leave'),
        }