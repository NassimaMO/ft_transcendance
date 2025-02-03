from django.db.models.signals import post_migrate
from django.dispatch import receiver
from matchmaker.models import Game, Rank
from .models import PongRank

@receiver(post_migrate)
def create_default_ranks(sender, **kwargs):
    if sender.name == "pong":
        pong, created = Game.objects.get_or_create(name="pong")
        Rank.objects.filter(game=pong).delete()
        marks = PongRank.marks_per_rank()
        for order, name in enumerate(PongRank.sorted_ranks(), start=1):
            Rank.objects.create(
                game=pong, 
                name=name, 
                order=order, 
                marks_required=marks.get(name, 0)
            )
