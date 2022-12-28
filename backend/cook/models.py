from administration.models import Ingredient, Tag
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=123,
    )
    author = models.ForeignKey(
        to=User,
        verbose_name="Автор рецепта",
        on_delete=models.CASCADE,
        related_name="recipes",
    )
    title = models.CharField(
        verbose_name="Название рецепта",
        max_length=50
    )
    text = models.TextField(
        verbose_name="Описание"
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления"
    )
    image = models.ImageField(
        verbose_name='Изображение блюда',
        upload_to='recipe_images/',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    slug = models.SlugField(unique=True)
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='Ingredientrecipe'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-pub_date"]

    def __str__(self):
        return self.title


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='ingredienttorecipe'
    )
    ingredient = models.ForeignKey(
        to=Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество ингредиента"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient",
            )
        ]

    def __str__(self):
        return (
            f"{self.ingredient.name} - {self.amount} "
            f"{self.ingredient.measurement_unit}"
        )
