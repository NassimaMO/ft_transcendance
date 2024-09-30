from django import forms
from .models import MatchChoice
from django.core.exceptions import NON_FIELD_ERRORS

import logging

logger = logging.getLogger('default')

class MatchChoiceForm(forms.ModelForm):

    class Meta:
        model = MatchChoice
        fields = ['mode', 'connect', 'mm']
        labels = {
            'connect': 'Connectivité',
            'mode': 'Mode de jeu',
            'mm': 'Matchmaking',
        }
        widgets = {
            'mode': forms.Select(attrs={'class': 'form-select'}),
            'connect': forms.Select(attrs={'class': 'form-select'}),
            'mm': forms.Select(attrs={'class': 'form-select'}),
        }

    def is_valid(self):
        valid = super().is_valid()
        if valid:
            return True
        if self.has_error(NON_FIELD_ERRORS, code="unique_together") :
            return True
        return False
    
    def save(self, commit=True):
        connect = self.cleaned_data.get('connect')
        mode = self.cleaned_data.get('mode')
        mm = self.cleaned_data.get('mm')
        try:
            instance = MatchChoice.objects.get(connect=connect, mode=mode, mm=mm)
            if commit :
                instance.save()
        except MatchChoice.DoesNotExist:
            instance = super().save(commit=commit)
        return instance
