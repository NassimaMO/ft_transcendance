from django import forms
from .models import MatchChoice
from django.core.exceptions import NON_FIELD_ERRORS

import logging

logger = logging.getLogger('default')

class MatchChoiceForm(forms.ModelForm):

    class Meta:
        model = MatchChoice
        fields = ['mode', 'connectivity', 'matchmaking']
        labels = {
            'connectivity': 'Connectivité',
            'mode': 'Mode de jeu',
            'matchmaking': 'Matchmaking',
        }
        widgets = {
            'mode': forms.Select(attrs={'class': 'form-select'}),
            'connectivity': forms.Select(attrs={'class': 'form-select'}),
            'matchmaking': forms.Select(attrs={'class': 'form-select'}),
        }

    def is_valid(self):
        valid = super().is_valid()
        if valid:
            return True
        if self.has_error(NON_FIELD_ERRORS, code="unique_together") :
            return True
        return False
    
    def save(self, commit=True):
        connectivity = self.cleaned_data.get('connectivity')
        mode = self.cleaned_data.get('mode')
        matchmaking = self.cleaned_data.get('matchmaking')
        try:
            instance = MatchChoice.objects.get(connectivity=connectivity, mode=mode, matchmaking=matchmaking)
            if commit :
                instance.save()
        except MatchChoice.DoesNotExist:
            instance = super().save(commit=commit)
        return instance
