from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from djoser.serializers import UserSerializer
from djoser.serializers import UserCreateSerializer

from api.fields import Base64ImageField
from cook.models import (IngredientRecipe, Recipe)
from administration.models import (Ingredient, Tag)
from cook.models import (IngredientRecipe, Recipe)
from print.models import FavoriteShoppingCart, ShoppingCart


from users.models import Follow, User


class CustomUserSerializer(UserSerializer):
    """Сериализатор просмотра профиля пользователя"""
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id", "email", "username", "first_name",
            "last_name", "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        """Проверяет подписку на текущего пользователя"""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """ Сериализатор создания пользователя """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name',
            'last_name', 'password')


class RecipeMiniSerializer(serializers.ModelSerializer):
    """Мини-сериализатор для просмотра рецептов в профиле пользователя"""
    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )


class SubscribeSerializer(UserSerializer):
    """ Сериализатор для создания/получения подписок """
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            "id", "email", "username", "first_name", "last_name",
            "is_subscribed", "recipes", "recipes_count",
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_is_subscribed(self, obj):
        """Проверяет подписку на текущего пользователя"""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=obj).exists()

    def get_recipes(self, obj):
        """Показывает рецепты текущего пользователя"""
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = RecipeMiniSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Счетчик рецептов текущего пользователя"""
        return obj.recipes.count()

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Follow.objects.filter(author=author, user=user).exists():
            raise serializers.ValidationError(
                detail='Подписка уже существует',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise serializers.ValidationError(
                detail='Нельзя подписаться на самого себя',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для GET запросов ингредиентов"""
    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()

    class Meta:
        model = IngredientRecipe
        fields = ("id", "name", "measurement_unit")


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для связной модели IngredientRecipe"""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания и просмотра тегов"""
    class Meta:
        model = Tag
        fields = (
            'id', 'name', "color", 'slug'
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра рецептов"""
    tags = TagSerializer(many=True)
    ingredients = IngredientRecipeSerializer(
        many=True, source='ingredientrecipes'
    )
    author = CustomUserSerializer()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = ('author',)

    def get_is_favorited(self, obj):
        """Проверяет добавлен ли рецепт в избранное
        у авторизованного пользователя"""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.shopping_list.filter(user=request.user).exists()


class RecipePostSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта"""
    tags = serializers.SlugRelatedField(
        slug_field="id",
        queryset=Tag.objects.all(),
        many=True,
        required=True
    )

    ingredients = IngredientRecipeSerializer(many=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name',
            'image', 'text', 'cooking_time'
        )
        read_only_fields = ('author',)

    def validate_ingredients(self, value):
        """Валидация поля ингредиентов при создании рецепта"""
        if not value:
            raise serializers.ValidationError(
                'Необходимо указать как минимум один ингредиент'
            )
        ingredients_id_list = []
        for item in value:
            if item['amount'] == 0:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть равным нулю'
                )
            ingredient_id = item['ingredient']['id']
            if ingredient_id in ingredients_id_list:
                raise serializers.ValidationError(
                    'Указано несколько одинаковых ингредиентов'
                )
            ingredients_id_list.append(ingredient_id)
        return value

    def validate_tags(self, value):
        """Валидаци поля тегов при создании рецепта"""
        if not value:
            raise serializers.ValidationError(
                'Необходимо указать как минимум один тег'
            )
        return value

    def _create_ingredient_recipe_objects(self, ingredients, recipe):
        """Вспомогательный метод для создания
        объектов модели IngredientRecipe"""
        for ingredient in ingredients:
            ingredient_amount = ingredient.pop("amount")
            ingredient_obj = get_object_or_404(
                Ingredient, id=ingredient['ingredient']['id']
            )
            IngredientRecipe.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredient_obj,
                amount=ingredient_amount
            )
            recipe.ingredients.add(ingredient_obj)
        return recipe

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        return self._create_ingredient_recipe_objects(ingredients, recipe)

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self._create_ingredient_recipe_objects(ingredients, recipe=instance)
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(instance, context=context).data


class FavoriteSerializer(RecipeSerializer):
    """Сериализатор для добавления рецепта в избранное"""
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta(RecipeSerializer.Meta):
        fields = ("id", "name", "image", "cooking_time")

    def validate(self, data):
        recipe = self.instance
        user = self.context.get('request').user
        if FavoriteShoppingCart.objects.filter(
            recipe=recipe, user=user
        ).exists():
            raise serializers.ValidationError(
                detail='Рецепт уже добавлен в избранное',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data


class ShoppingCartSerializer(RecipeSerializer):
    """Сериализатор добавления рецепта в корзину"""
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta(RecipeSerializer.Meta):
        fields = ("id", "name", "image", "cooking_time")

    def validate(self, data):
        recipe = self.instance
        user = self.context.get('request').user
        if ShoppingCart.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError(
                detail='Рецепт уже добавлен в корзину',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data
