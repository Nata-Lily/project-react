from django.contrib import admin

from .models import IngredientRecipe, Recipe


class IngredientInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 3
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'name',
        'cooking_time',
        'get_favorites',
        'get_ingredients',
    )
    search_fields = (
        'name',
        'author',
        'tags'
    )
    list_filter = (
        'author',
        'name',
        'tags'
    )
    inlines = (IngredientInline,)
    empty_value_display = '-пусто-'

    def get_favorites(self, obj):
        return obj.favorites.count()
    get_favorites.short_description = 'Избранное'

    def get_ingredients(self, obj):
        return ', '.join([
            ingredients.name for ingredients
            in obj.ingredients.all()])
    get_ingredients.short_description = 'Ингредиенты'
