from django import forms
from .models import MessOption, Leave
from django.forms.widgets import TextInput, Textarea
from django.utils.translation import ugettext_lazy as _

class MessForm(forms.ModelForm):
    class Meta:
        model = MessOption
        fields = ['mess']

class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        exclude = ['student', 'approvedBy', 'approved', 'comment']
        widgets = {
            'dateTimeStart': forms.TextInput(attrs={'class': 'datepicker'}),
            'dateTimeEnd': forms.TextInput(attrs={'class': 'datepicker'}),
            'reason': forms.Textarea(attrs={'class': 'materialize-textarea'}),
            'corrAddress': forms.Textarea(attrs={'class': 'materialize-textarea'}),
        }
        labels = {
            'dateTimeStart': _('Departure Date'),
            'dateTimeEnd': _('Arrival Date'),
            'consent': _('Parent Consent Type'),
            'corrAddress': _('Address for Correspondence during Leave'),
            'corrPhone': _('Contact No. during Leave'),
        }
