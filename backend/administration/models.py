from django.db import models
from django.core.validators import RegexValidator
from django.db.models import CharField


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Название ингредиента",
        max_length=100,
        db_index=True
    )
    measurement_unit = models.CharField(
        max_length=30,
        verbose_name="Единица иземерения"
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        max_length=8,
        verbose_name='Название тега',
        db_index=True,
        unique=True
    )
    slug = models.SlugField(
        unique=True,
        max_length=50,
        verbose_name='Slug',
        blank=True
    )
    color = CharField(
        verbose_name='HEX-код',
        max_length=7,
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name
