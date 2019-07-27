from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from recipe.serialisers import IngredientSerializer
from core.models import Ingredient
INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientTest(TestCase):
    """test public aceess """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """check login required"""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngerdientTests(TestCase):
    """test private access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('t@t.com', 'somepass')
        self.client.force_authenticate(self.user)

    def test_retrieve_ingradients(self):
        """retrieve ingredients"""
        Ingredient.objects.create(user=self.user, name='Paneer')
        Ingredient.objects.create(user=self.user, name='Aloo')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serialiser = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serialiser.data)

    def tst_user_ingredients(self):
        """rertrive user ingredients"""
        get_user_model().objects.create_user(
            'new@new.com', 'newuser')

        Ingredient.objects.create(user=self.user, name='Capsicum')

        ingredients = Ingredient.objects.create(user=self.user, name='Tomato')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredients.name)

    def test_create_ingredient(self):
        """create ingredients"""
        payload = {'name': 'Rice'}
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.all().filter(
            user=self.user, name=payload['name']).exists()
        self.assertTrue(exists)

    def test_invalid_create(self):
        """test invalid creatation"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)
        self.assertTrue(res.status_code, status.HTTP_400_BAD_REQUEST)
