from django import forms
from .models import MatchChoice, GameMode, Connectivity, MatchmakingMode, Game
from django.core.exceptions import NON_FIELD_ERRORS

import logging

logger = logging.getLogger('default')

class MatchChoiceForm(forms.ModelForm):

    class Meta:
        model = MatchChoice
        fields = ['game', 'mode', 'connectivity', 'matchmaking', 'auto_fill']

    def is_valid(self):
        valid = super().is_valid()
        if valid:
            return True
        if self.has_error(NON_FIELD_ERRORS, code="unique_together") :
            return True
        return False
    
    def save(self, commit=True):
        game = self.cleaned_data.get('game')
        connectivity = self.cleaned_data.get('connectivity')
        mode = self.cleaned_data.get('mode')
        matchmaking = self.cleaned_data.get('matchmaking')
        auto_fill = self.cleaned_data.get('auto_fill')
        try:
            instance = MatchChoice.objects.get(game=game, connectivity=connectivity, mode=mode, matchmaking=matchmaking, auto_fill=auto_fill)
        except MatchChoice.DoesNotExist:
            instance = super().save(commit=commit)
        return instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['game'].label_from_instance = lambda obj: obj.name.capitalize()
        self.fields['auto_fill'].widget.attrs['disabled'] = True
        mode = self.initial.get('mode', None)
        connectivity = self.initial.get('connectivity', None)
        if mode == GameMode.SOLO or mode == GameMode.MULTI_1V1 or connectivity == Connectivity.LOCAL:
            self.fields['auto_fill'].widget.attrs['hidden'] = True

    def clean(self):
        cleaned_data = super().clean()
        mode = cleaned_data.get("mode")
        connectivity = cleaned_data.get("connectivity")
        matchmaking = cleaned_data.get("matchmaking")
        auto_fill = cleaned_data.get("auto_fill")
        if mode == GameMode.SOLO:
            if connectivity != Connectivity.LOCAL:
                self.add_error("connectivity", "La connectivité doit être locale pour ce choix de modes.")
            if matchmaking != MatchmakingMode.UNRANK:
                self.add_error("matchmaking", "Le matchmaking doit être non classé pour ce choix de modes.")
        if auto_fill is True and mode == GameMode.SOLO or mode == GameMode.MULTI_1V1 or connectivity == Connectivity.LOCAL :
            self.add_error("auto_fill", "Le remplissage automatique doit être désactivé pour ce choix de modes.")
        return cleaned_data
