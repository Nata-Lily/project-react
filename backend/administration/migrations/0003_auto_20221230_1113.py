# Generated by Django 3.2.16 on 2022-12-30 04:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0002_auto_20221230_1011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
