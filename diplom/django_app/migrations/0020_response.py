# Generated by Django 4.2.7 on 2023-11-05 09:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_app', '0019_remove_product_image_product_image_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vacancy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_app.vacancy')),
                ('work', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_app.work')),
            ],
        ),
    ]
