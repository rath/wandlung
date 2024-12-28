# Generated by Django 5.1.4 on 2024-12-28 21:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0004_alter_settings_options_alter_youtubevideo_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subtitle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(choices=[('en', 'English'), ('ko', 'Korean'), ('de', 'German')], max_length=2)),
                ('is_transcribed', models.BooleanField(default=True)),
                ('content', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subtitles', to='apps.youtubevideo')),
            ],
            options={
                'verbose_name': 'Subtitle',
                'verbose_name_plural': 'Subtitles',
                'unique_together': {('video', 'language')},
            },
        ),
    ]