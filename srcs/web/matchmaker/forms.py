from django import forms
from .models import MatchChoice, GameMode, Connectivity, MatchmakingMode, Lobby
from django.core.exceptions import NON_FIELD_ERRORS

import logging

logger = logging.getLogger('default')

class MatchChoiceForm(forms.ModelForm):
    class Meta:
        model = MatchChoice
        fields = ['game', 'mode', 'connectivity', 'matchmaking']

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
        try:
            instance = MatchChoice.objects.get(game=game, connectivity=connectivity, mode=mode, matchmaking=matchmaking)
        except MatchChoice.DoesNotExist:
            instance = super().save(commit=commit)
        return instance

    def __init__(self, is_edit=False, *args, **kwargs):
        self.is_edit = is_edit
        super().__init__(*args, **kwargs)
        self.fields['game'].label_from_instance = lambda obj: obj.name.capitalize()

    def clean(self):
        cleaned_data = super().clean()
        mode = cleaned_data.get("mode")
        connectivity = cleaned_data.get("connectivity")
        matchmaking = cleaned_data.get("matchmaking")
        if mode == GameMode.SOLO:
            if connectivity != Connectivity.LOCAL:
                self.add_error("connectivity", "La connectivité doit être locale pour ce choix de modes.")
            if matchmaking != MatchmakingMode.UNRANK:
                self.add_error("matchmaking", "Le matchmaking doit être non classé pour ce choix de modes.")
        return cleaned_data


class LobbyForm(MatchChoiceForm):
    auto_fill = forms.BooleanField(required=False)

    def __init__(self, instance=None, is_edit=False, *args, **kwargs):
        if instance:
            super().__init__(instance=instance.match_choice, *args, **kwargs)
            self.is_edit = is_edit
            if not self.is_edit:
                self.fields['auto_fill'].widget.attrs['id'] = f"default_id_auto_fill"
                self.fields['auto_fill'].widget.attrs['disabled'] = True
            mode = instance.match_choice.mode
            connectivity = instance.match_choice.connectivity
            if mode == GameMode.SOLO or mode == GameMode.MULTI_1V1 or connectivity == Connectivity.LOCAL or \
                instance.members_count(include_autofill=False) == instance.match_choice.players_required() / 2:
                self.fields['auto_fill'].widget.attrs['hidden'] = True
            else:
                self.fields['auto_fill'].widget.attrs['hidden'] = False
            self.initial['auto_fill'] = instance.auto_fill
    
    def clean(self):
        cleaned_data = super().clean()
        auto_fill = cleaned_data.get("auto_fill")
        mode = cleaned_data.get("mode")
        connectivity = cleaned_data.get("connectivity")
        if auto_fill is True and mode == GameMode.SOLO or mode == GameMode.MULTI_1V1 or connectivity == Connectivity.LOCAL :
            self.add_error("auto_fill", "Le remplissage automatique doit être désactivé pour ce choix de modes.")
