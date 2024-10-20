from django.contrib.auth import get_user_model
from django.test import TestCase
from cats.models import Cat, Breed

from django.db.utils import IntegrityError

User = get_user_model()

class CatModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='Bob')
        self.breed = Breed.objects.create(name='scottish fold')
        self.cat = Cat.objects.create(name='Cathy', age=37, color='black', owner=self.user, breed=self.breed, description='')

    def test_cat_owner_relationship(self):
        self.assertEqual(self.cat.owner.username, 'Bob')

    def test_cat_breed_relationship(self):
        self.assertEqual(self.cat.breed.name, 'scottish fold')
 
            