from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from rest_framework import serializers
from .models import Cat, Breed, Rating


class CatSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    breed = serializers.CharField()
    description = serializers.CharField(default='')
    age = serializers.IntegerField(min_value=1, max_value=240)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Cat
        fields = ['id', 'name', 'age', 'color', 'description', 'breed', 'owner', 'average_rating']

    def create(self, validated_data):
        return Cat.objects.create_cat(
            name=validated_data['name'],
            age=validated_data['age'],
            color=validated_data['color'],
            breed=validated_data['breed'].lower(),
            owner=validated_data['owner'],
            description=validated_data['description']
        )
    
    def get_average_rating(self, obj):
        return obj.avg_rating
    

class BreedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Breed
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    ownership = CatSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'ownership']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user
    

class RatingSerializer(serializers.ModelSerializer):
    value = serializers.FloatField()
    cat = serializers.PrimaryKeyRelatedField(queryset=Cat.objects.all())

    class Meta:
        model = Rating
        fields = ['cat', 'value']

    def validate_value(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError('The rating value must be between 1.0 and 10.0')
        return value
        
    def create(self, validated_date):
        request = self.context.get('request')
        user = request.user

        try:
            rating = Rating.objects.create(user=user, **validated_date)
        except IntegrityError:
            raise serializers.ValidationError("You've already rated this cat.")
        return rating
    


    
