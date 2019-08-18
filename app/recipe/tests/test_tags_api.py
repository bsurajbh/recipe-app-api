from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serialisers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@londonappdev.com',
            'password'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(name='Vegan', user=self.user)
        Tag.objects.create(name='Dessert', user=self.user)

        res = self.client.get(TAGS_URL)
        # print(res)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for authenticated user"""
        user2 = get_user_model().objects.create_user(
            'other@londonappdev.com',
            'testpass'
        )
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_retrieve_tags_assigned_to_recipe(self):
        """get tags assigned to recipee"""
        tag1 = Tag.objects.create(user=self.user, name='Lunch')
        tag2 = Tag.objects.create(user=self.user, name='Dinner')
        recipe = Recipe.objects.create(
            title='Methi paratha',
            time_minute=10,
            price=5.00,
            user=self.user
        )
        recipe.tags.add(tag1)
        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        serialiser1 = TagSerializer(tag1)
        serialiser2 = TagSerializer(tag2)

        self.assertIn(serialiser1.data, res.data)
        self.assertNotIn(serialiser2.data, res.data)

    def test_unique_tags_assigned_to_recipe(self):
        """assigned returns unique items"""
        tag1 = Tag.objects.create(user=self.user, name='Lunch')
        # tag2 = Tag.objects.create(user=self.user, name='Dinner')
        recipe = Recipe.objects.create(
            title='Methi paratha',
            time_minute=10,
            price=5.00,
            user=self.user
        )
        recipe.tags.add(tag1)
        recipe2 = Recipe.objects.create(
            title='Methi paratha',
            time_minute=10,
            price=5.00,
            user=self.user
        )
        recipe2.tags.add(tag1)
        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
