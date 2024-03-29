from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
USER_URL = reverse('user:user')

# helper function


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """test public urls api"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """create user successful wirh valid params or payload"""
        payload = {
            'email': 'someuser@test.com',
            'password': 'testpass',
            'name': 'some name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_duplicate_user(self):
        """create duplicate user"""
        payload = {
            'email': 'someuser@test.com',
            'password': 'testpass',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_small(self):
        """ test small length passsword """
        payload = {
            'email': 'someuser@test.com',
            'password': 'pa',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        # user not created
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertFalse(user_exists)

    def test_create_token(self):
        """test token creation user"""
        payload = {
            'email': 'someuser@test.com',
            'password': 'testpass',
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_failure_token(self):
        """test wrong password and toen condition"""
        payload = {
            'email': 'someuser@test.com',
            'password': 'testpass',
        }
        create_user(**payload)
        payload = {
            'email': 'someuser@test.com',
            'password': 'wrong pass',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_user_exists_token(self):
        """create token without user in db"""
        payload = {
            'email': 'someuser@test.com',
            'password': 'wrong pass',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorised_access(self):
        """make unauthorised request"""
        res = self.client.get(USER_URL, {})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserTests(TestCase):
    """authetication require tests"""

    def setUp(self):
        self.user = create_user(
            email='asdf@a.com',
            password='somepass',
            name='testname'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_user_profile(self):
        """get user form db"""
        res = self.client.get(USER_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_request_not_allowed(self):
        """post not allowed"""
        res = self.client.post(USER_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_profile(self):
        """update user profile"""
        payload = {
            'name': 'new user name',
            'password': 'newuserpassword'
        }
        res = self.client.patch(USER_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
