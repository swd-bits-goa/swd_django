from django import forms
from .models import MessOption, Leave, Bonafide, DayPass
from django.forms.widgets import TextInput, Textarea, FileInput
from django.utils.translation import ugettext_lazy as _
from datetime import date, datetime, timedelta


class MessForm(forms.ModelForm):
    class Meta:
        model = MessOption
        fields = ['mess']

class MessBillForm(forms.Form):
    dateStart = forms.CharField(label='Start Date', widget=forms.TextInput(attrs={'class': 'datepicker mask'}))
    dateEnd = forms.CharField(label='End Date', widget=forms.TextInput(attrs={'class': 'datepicker mask'}))

    def clean(self):
        cleaned_data = super().clean()
        if("dateStart" not in cleaned_data or "dateEnd" not in cleaned_data):
            return cleaned_data

        dateStart = datetime.strptime(cleaned_data['dateStart'], '%d %B, %Y').date()
        dateEnd = datetime.strptime(cleaned_data['dateEnd'], '%d %B, %Y').date()
        if (dateStart > dateEnd):
            self.add_error('dateEnd', "End Date must be after Start Date")
        if (dateStart > date.today()):
            self.add_error('dateStart', "Start Date must be before today")
        if (dateEnd > date.today()):
            self.add_error('dateEnd', "End Date must be before today")
        
        return cleaned_data

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
        if (date_time_start - datetime.now()) <= timedelta(hours=10):
           self.add_error('dateStart', "Cannot apply for leave one day before departure. Contact warden for immediate leave approval")
        if (dateStart - dateEnd).days == 0:
            self.add_error('dateStart', "Start date and end date cannot be the same. Apply for a day pass instead")
        return cleaned_data

    class Meta:
        model = Leave
        exclude = ['dateTimeStart', 'dateTimeEnd', 'student',
                   'approvedBy', 'approved', 'disapproved', 'inprocess',
                   'comment', 'corrPhone', 'claimed']

        widgets = {
            'reason': forms.Textarea(attrs={'class': 'materialize-textarea validate'}),
            'corrAddress': forms.Textarea(attrs={'class': 'materialize-textarea validate'}),
        }
        labels = {
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
    date = forms.CharField(label='Date', widget=forms.TextInput(attrs={'class': 'datepicker mask'}))
    time = forms.CharField(label='Out Time', widget=forms.TextInput(attrs={'class': 'timepicker mask'}))
    intime = forms.CharField(label='In Time', widget=forms.TextInput(attrs={'class': 'timepicker mask'}))
    document = forms.FileField(
            label="Any Supporting Document",
            required=False,
            widget=forms.FileInput(attrs={'class': 'file-field input-field'})
    )
    
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
    out_date = forms.CharField(
        label='Out Date',
        widget=forms.TextInput(attrs={'class': 'datepicker mask'})
    )
    # in_date field is removed entirely

    def __init__(self, *args, **kwargs):
        # Remove logic related to existing_in_date as the field is gone
        super(VacationLeaveNoMessForm, self).__init__(*args, **kwargs)

    def clean_out_date(self):
        """ Basic format validation for the out_date """
        out_date_str = self.cleaned_data.get('out_date')
        if out_date_str:
            try:
                # Validate the date format
                datetime.strptime(out_date_str, '%d %B, %Y').date()
            except ValueError:
                raise forms.ValidationError("Invalid date format. Use DD Month, YYYY.")
        return out_date_str

    # clean method is simplified as in_date is not part of the form's data
    def clean(self):
        cleaned_data = super(VacationLeaveNoMessForm, self).clean()
        # The comparison between out_date and in_date will now happen in the view
        # as the form doesn't know the required in_date.
        return cleaned_data

