# Generated by Django 4.2.3 on 2024-08-10 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_alter_user_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='division',
            field=models.IntegerField(default=4),
        ),
        migrations.AddField(
            model_name='user',
            name='mark',
            field=models.IntegerField(default=0),
        ),
    ]
