# Generated by Django 5.0.6 on 2024-06-28 13:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GameSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.TextField(max_length=125)),
                ('score', models.IntegerField(default=0)),
                ('started', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, max_length=125, null=True)),
                ('level', models.FloatField(default=0)),
                ('rank', models.IntegerField(default=0)),
                ('gamesWon', models.FloatField(default=0)),
                ('gamesTotal', models.FloatField(default=0)),
                ('gamesWonMulti', models.FloatField(default=0)),
                ('gamesWonRegular', models.FloatField(default=0)),
                ('GameHistory', models.ManyToManyField(related_name='gameSessions', through='api.GameSession', to='api.player')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='gamesession',
            name='player_one',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_one', to='api.player'),
        ),
        migrations.AddField(
            model_name='gamesession',
            name='player_two',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='player_two', to='api.player'),
        ),
        migrations.CreateModel(
            name='Friend',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friend_from', to=settings.AUTH_USER_MODEL)),
                ('user_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friend_to', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user_from', 'user_to')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='gamesession',
            unique_together={('player_one', 'player_two')},
        ),
    ]