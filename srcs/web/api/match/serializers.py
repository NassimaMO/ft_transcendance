from rest_framework import serializers
from matchmaker.models import MatchChoice

import logging

logger = logging.getLogger('default')

class MatchChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchChoice
        fields = ['connect', 'mode', 'mm']

    def is_valid(self):
        valid = super().is_valid()
        if valid:
            return True
        if self.errors.get("non_field_errors") :
            for error in self.errors["non_field_errors"] :
                if error.code != "unique" :
                    return False
            return True
        return False

    def save(self, **kwargs):
        match_choice = MatchChoice.objects.filter(**kwargs).first()
        if match_choice:
            return match_choice
        return super().save(**kwargs)