# Generated by Django 3.2.16 on 2023-01-11 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0004_alter_tag_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Название ингредиента'),
        ),
    ]
