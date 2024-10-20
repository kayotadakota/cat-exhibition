from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields.generated import GeneratedField

# Create your models here.
class CatManager(models.Manager):
    
    def create_cat(self, name, age, color, breed, owner, description=''):
        breed_name, created = Breed.objects.get_or_create(name=breed)
        cat = Cat(
            name=name,
            age=age,
            color=color,
            breed=breed_name,
            owner=owner,
            description=description
        )
        cat.save()
        return cat


class Breed(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name
   

class Cat(models.Model):
    name = models.CharField(max_length=64, blank=False, null=False)
    age = models.IntegerField() # in months
    color = models.CharField(max_length=64)
    description = models.CharField(max_length=255, default='', blank=True, null=True)
    breed = models.ForeignKey(Breed, on_delete=models.RESTRICT)
    owner = models.ForeignKey(User, related_name='ownership', on_delete=models.CASCADE)
    # avg_rating = models.ManyToManyField(User, through='Rating')
    objects = CatManager()

    def __str__(self):
        return f'Name: {self.name}, Breed: {self.breed}'

    def save(self, *args, **kwargs):
        # If the name value is an empty string set it to 'unknown'.
        if not self.name or not self.name.strip():
            self.name = 'unknown'
        # If the specified breed already exists get that breed.
        super().save(*args, **kwargs)

    @property
    def avg_rating(self):
        ratings = self.rating_set.all()
        if ratings:
            return round(sum(rating.value for rating in ratings) / len(ratings), 1)
        return 0.0
    
    
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE)
    value = models.FloatField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'cat'], name='cat-rating')
        ]
    
    def __str__(self):
        return f'{self.user} | {self.cat.name} | {self.value}'

