import unittest
from django.test import Client, TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from cats.models import Breed, Cat


class BaseConfig(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='username', password='password')
        self.breed = Breed.objects.create(name='scottish fold')
        self.cat = Cat.objects.create(name='Tom', age=37, color='black', breed=self.breed, owner=self.user)


class RegisterUserTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_register_new_user(self):
        # Send a POST request with credentials.
        response = self.client.post('/api/user/register/', {'username': 'username', 'password': 'password'})
        # Check that the response code is 201.
        self.assertEqual(response.status_code, 201)

    def test_user_already_exists(self):
        # Send a POST request to create the first user.
        response = self.client.post('/api/user/register/', {'username': 'username', 'password': 'password'})
        # Check that the response code is 201.
        self.assertEqual(response.status_code, 201)
        # Send another POST request with the same credentials.
        response = self.client.post('/api/user/register/', {'username': 'username', 'password': 'password'})
        # Check that the response code is 400.
        self.assertEqual(response.status_code, 400)


class UserListTest(BaseConfig):

    def test_user_list(self):
        # Send a GET request for the user list.
        response = self.client.get('/api/users/')
        # Check that the response code is 200.
        self.assertEqual(response.status_code, 200)
        # Check that there is one user created.
        self.assertEqual(len(response.json()), 1)


class BreedListTest(BaseConfig):

    def test_breed_list(self):
        # Send a GET request for the breed list.
        response = self.client.get('/api/breeds/')
        # Check that the response code is 200.
        self.assertEqual(response.status_code, 200)
        # Check that there is one breed created.
        self.assertEqual(len(response.json()), 1)


class CatListTest(BaseConfig):
    
    def test_cat_list(self):
        # Send a GET request for the cat list.
        response = self.client.get('/api/cats/')
        # Check that the response code is 200.
        self.assertEqual(response.status_code, 200)
        # Check that there is one cat created.
        self.assertEqual(len(response.json()), 1)


class CatListByBreedTest(BaseConfig):

    def test_cat_list_by_breed(self):
        # Send a GET request for the cat list with specified ID.
        response = self.client.get('/api/cats/breed/1')
        # Check that the response code is 200.
        self.assertEqual(response.status_code, 200)
        # Check that there is one cat with specified breed.
        self.assertEqual(len(response.json()), 1)


class AddCatTest(BaseConfig):

    def setUp(self):
        super().setUp()
        self.payload = {
            'name': 'Cathy',
            'age': 37,
            'color': 'black',
            'description': '',
            'owner': self.user,
            'breed': 'scottish fold'
        }

    def test_create_cat_without_auth(self):
        '''Unauthorized user must fail to create a new cat object.'''
        response = self.client.post('/api/cat/add/', data=self.payload)
        # Check that the response code is 401.
        self.assertEqual(response.status_code, 401)

    def test_create_cat_with_auth(self):
        # Register a new user.
        response = self.client.post('/api/user/register/', data={'username': 'bob', 'password':'password'})
        self.assertEqual(response.status_code, 201)
        # Get a JSON Web Token.
        response = self.client.post('/api/token/', data={'username': 'bob', 'password': 'password'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        access_token = data.get('access')
        # Attach received token to the headers.
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        # Create a new instance of the Cat object.
        response = self.client.post('/api/cat/add/', data=self.payload)
        # Check that the reponse code is 201.
        self.assertEqual(response.status_code, 201)


class CatDetailsTest(BaseConfig):

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)

    def _switch_user(self):
        user = User.objects.create_user(username='Bob', password='password')
        self.client.force_authenticate(user=user)

    def test_get_cat_details(self):
        # Send a GET request for the cat's details with specified ID.
        response = self.client.get('/api/cat/details/1')
        # Check that the response code is 200.
        self.assertEqual(response.status_code, 200)

    def test_get_cat_details_not_found(self):
        # Send a GET request for the cat's details that isn't exist.
        response = self.client.get('/api/cat/details/99')
        # Check that the response code is 404.
        self.assertEqual(response.status_code, 404)

    def test_update_owned_cat_details(self):
        # Send a PUT request to upgrade the details of the cat with specified ID.
        payload = {
            'name': 'kristine'
        }
        response = self.client.put('/api/cat/details/1', data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'kristine')

    def test_update_not_owned_cat_details(self):
        # Try to change the details of someone's cat.
        self._switch_user()
        response = self.client.put('/api/cat/details/1', data={'name': "bob's cat"})
        self.assertEqual(response.status_code, 403)

    def test_delete_cat(self):
        # Send a DELETE request to remove the cat with specified ID.
        response = self.client.delete('/api/cat/details/1')
        self.assertEqual(response.status_code, 204)

        