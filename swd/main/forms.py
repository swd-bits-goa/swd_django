from django import forms
from .models import MessOption

class MessForm(forms.ModelForm):
    class Meta:
        model = MessOption
        fields = ['mess']