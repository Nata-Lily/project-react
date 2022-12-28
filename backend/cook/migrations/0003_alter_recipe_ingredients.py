# Generated by Django 3.2.16 on 2022-12-27 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0001_initial'),
        ('cook', '0002_alter_recipe_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(through='cook.IngredientRecipe', to='administration.Ingredient', verbose_name='Ингредиенты'),
        ),
    ]