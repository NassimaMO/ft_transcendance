# Generated by Django 4.2.3 on 2024-08-18 17:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matchmaker', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MatchChoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('connect', models.CharField(choices=[('multi local', 'Multijoueur Local'), ('multi online', 'Multijoueur en ligne')], default='multi local', max_length=20)),
                ('mode', models.CharField(choices=[('solo', 'Un joueur (VS IA)'), ('multi', 'Multijoueur')], default='solo', max_length=20)),
                ('mm', models.CharField(choices=[('ranked', 'Ranked'), ('unranked', 'Unranked'), ('tournament', 'Tournament')], default='unranked', max_length=20)),
            ],
        ),
        migrations.RemoveField(
            model_name='match',
            name='mm',
        ),
        migrations.RemoveField(
            model_name='match',
            name='mode',
        ),
        migrations.AddField(
            model_name='match',
            name='info',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='match_info', to='matchmaker.matchchoice'),
            preserve_default=False,
        ),
    ]
