# Generated by Django 4.2.6 on 2023-10-30 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_app', '0006_vacancy_face_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vacancy',
            name='face_photo',
            field=models.ImageField(blank=True, null=True, upload_to='media/face_photos/'),
        ),
    ]
