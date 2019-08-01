from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
from rest_framework import status
from recipe.serialisers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def sample_tag(user, name='Main course'):
    """sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Carrot'):
    """"sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def detail_url(recipe_id):
    """return details of recipe"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_recipe(user, **params):
    """create recipe"""
    defaults = {
        'title': 'paneer tikka',
        'time_minute': 10,
        'price': 5.00
    }
    defaults.update(**params)
    return Recipe.objects.create(user=user, **defaults)
# public test


class PublicRecipeTests(TestCase):
    """public api test for recipe"""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_recipe(self):
        """retrieve unauthorised recipee"""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeTests(TestCase):
    """authorised test cases"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@some.com', password='testsomeuser')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe(self):
        """retrieve recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipe = Recipe.objects.all().order_by('-id')
        serialiser = RecipeSerializer(recipe, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialiser.data)

    def test_user_recipe(self):
        """retrieve user recipes"""
        usernew = get_user_model().objects.create_user(
            'somenewuser@testcom',
            'somenewpasword'
        )
        sample_recipe(user=self.user)
        sample_recipe(usernew)
        res = self.client.get(RECIPE_URL)

        recipe = Recipe.objects.filter(user=self.user)
        serialiser = RecipeSerializer(recipe, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialiser.data)
        self.assertTrue(len(res.data), 1)

    def test_recipe_detail(self):
        """see details of recipe"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serialiser = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serialiser.data)
