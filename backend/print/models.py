from cook.models import Recipe
from django.db import models
from django.db.models import UniqueConstraint
from Users.models import User


class FavoriteShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',

    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(app_label)s_%(class)s_unique'
            )
        ]

    def __str__(self):
        return f'{self.user} :: {self.recipe}'


class Favorite(FavoriteShoppingCart):
    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(FavoriteShoppingCart):
    class Meta(FavoriteShoppingCart.Meta):
        default_related_name = 'shopping_list'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
