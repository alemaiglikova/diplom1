# Generated by Django 4.2.7 on 2023-11-05 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_app', '0020_response'),
    ]

    operations = [
        migrations.AddField(
            model_name='work',
            name='responses',
            field=models.ManyToManyField(blank=True, related_name='work_responses', to='django_app.vacancy'),
        ),
        migrations.DeleteModel(
            name='Response',
        ),
    ]