# Generated by Django 4.2.6 on 2023-11-01 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_app', '0011_review_author'),
    ]

    operations = [
        migrations.CreateModel(
            name='Work',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('requirements', models.TextField()),
                ('contacts', models.CharField(max_length=100)),
                ('publish_date', models.DateField()),
                ('published_by', models.CharField(max_length=50)),
            ],
        ),
    ]
