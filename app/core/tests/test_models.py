from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


class ModelTests(TestCase):
    def test_create_user_email_successful(self):
        """create user with email successfully"""
        email = 'someemail@some.com'
        password = 'somepass'
        user = get_user_model().objects.create_user(
            email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_email_normalised(self):
        """email normalised test"""
        email = 'asdf@ASDF.COM'
        user = get_user_model().objects.create_user(email, '12345d00')

        self.assertEqual(user.email, email.lower())

    def test_email_invalid(self):
        """create user with no email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, '12346sa0')

    def test_new_superuser(self):
        """creating superuser"""
        user = get_user_model().objects.create_superuser(
            'asdfg@adf.com', '123ad123')

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    # tags test cases

    def test_tag_str_type(self):
        """str representation of tag model"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )
        self.assertEqual(str(tag), tag.name)

    # ingredients

    def test_ingedient_model(self):
        """"test ingredients model"""
        ingredients = models.Ingredient.objects.create(
            name='tomato', user=sample_user()
        )
        self.assertEqual(str(ingredients), ingredients.name)


def sample_user(email='testuser@testuser.com', password='testpass'):
    """create sample user for test"""
    return get_user_model().objects.create_user(email, password)
