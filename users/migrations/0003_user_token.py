# Generated by Django 4.2.2 on 2024-05-14 21:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_options_alter_user_avatar_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='token',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Token'),
        ),
    ]