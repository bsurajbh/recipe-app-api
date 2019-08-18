import tempfile
import os
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
from rest_framework import status
from recipe.serialisers import RecipeSerializer, RecipeDetailSerializer
from PIL import Image


RECIPE_URL = reverse('recipe:recipe-list')


def image_upload_url(recipe_id):
    """create upload url"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


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


class ImageUploadTest(TestCase):
    """Image upload tests"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'someuser@some.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        """after test method """
        self.recipe.image.delete()

    def test_image_upload(self):
        """upload image test"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            test_image = Image.new('RGB', (10, 10))
            test_image.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_by_tags(self):
        """filter recipe with tags"""
        recipe1 = sample_recipe(user=self.user, title='Paneer tikka')
        recipe2 = sample_recipe(user=self.user, title='Paneer masala')
        tag1 = sample_tag(user=self.user, name='vegan')
        tag2 = sample_tag(user=self.user, name='vegetarian')
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        recipe3 = sample_recipe(user=self.user, title="chicken")

        paylaod = {'tags': f'{tag1.id},{tag2.id}'}

        res = self.client.get(RECIPE_URL, paylaod)

        serialiser1 = RecipeSerializer(recipe1)
        serialiser2 = RecipeSerializer(recipe2)
        serialiser3 = RecipeSerializer(recipe3)

        self.assertIn(serialiser1.data, res.data)
        self.assertIn(serialiser2.data, res.data)
        self.assertNotIn(serialiser3.data, res.data)

    def test_filter_by_ingredients(self):
        """filter recipe with tags"""
        recipe1 = sample_recipe(user=self.user, title='Paneer tikka')
        recipe2 = sample_recipe(user=self.user, title='Paneer masala')
        ingredient1 = sample_ingredient(user=self.user, name='soda')
        ingredient2 = sample_ingredient(user=self.user, name='pickle')
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        recipe3 = sample_recipe(user=self.user, title="mashrooms")

        paylaod = {'ingredients': f'{ingredient1.id},{ingredient2.id}'}

        res = self.client.get(RECIPE_URL, paylaod)

        serialiser1 = RecipeSerializer(recipe1)
        serialiser2 = RecipeSerializer(recipe2)
        serialiser3 = RecipeSerializer(recipe3)

        self.assertIn(serialiser1.data, res.data)
        self.assertIn(serialiser2.data, res.data)
        self.assertNotIn(serialiser3.data, res.data)
