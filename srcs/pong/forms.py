from django import forms
from matchmaker.models import MatchChoice, GameMode, Connecitvity, MatchmakingMode

class MatchChoiceForm(forms.ModelForm):
    class Meta:
        model = MatchChoice
        fields = ['mode', 'connect', 'mm']
        labels = {
            'connect': 'Type de connexion',
            'mode': 'Mode de jeu',
            'mm': 'Mode de matchmaking',
        }
        widgets = {
            'mode': forms.Select(attrs={'class': 'form-select'}),
            'connect': forms.Select(attrs={'class': 'form-select'}),
            'mm': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super(MatchChoiceForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()       
        return cleaned_data
