# Generated by Django 3.0.5 on 2020-04-22 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processing', '0003_auto_20200422_2146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='ratio',
            field=models.IntegerField(blank=True, default=75),
        ),
    ]
