from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .serializers import CatSerializer, BreedSerializer, UserSerializer, RegisterSerializer, RatingSerializer
from django.contrib.auth.models import User
from .models import Breed, Cat

from django.shortcuts import get_object_or_404
from .permissions import IsOwnerOrReadOnly

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiExample,
    OpenApiResponse,

)

# Create your views here.

class RegisterUser(APIView):

    @extend_schema(
        summary="New user registration",
        description="Creates a new user. Each user has the list of owned cats.",
        request=UserSerializer,
        responses={
            201: OpenApiResponse(response=UserSerializer, description='User registered successfully.'),
            400: OpenApiResponse(description='Validation error.')
        },
        examples=[
            OpenApiExample(
                name='Request example',
                value={'username': 'username', 'password': 'password'},
                request_only=True
            )
        ],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'User registered successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@extend_schema_view(
    get=extend_schema(
        summary="User list",
        description="Returns the list of all existing users.",
        examples=[
            OpenApiExample(
                name='/api/users/',
                value={'id': 1, 'username': 'username', 'ownership': [{
                    'id': 1,
                    'name': 'Cathy',
                    'age': 37,
                    'color': 'grey',
                    'description': 'lovely cat',
                    'breed': 'scottish fold',
                    'owner': 'username'
                }]}
            )
        ]
    )
)
class UserList(generics.ListAPIView):
    queryset = User.objects.prefetch_related('ownership')
    serializer_class = UserSerializer


@extend_schema_view(
    get=extend_schema(
        summary='Breed list',
        description="Returns the list of all existing breeds.",
        examples=[
            OpenApiExample(
                name='/api/breeds/',
                value={'id': 1, 'name': 'siamese'}
            )
        ]
    )
)
class BreedList(generics.ListAPIView):
    queryset = Breed.objects.all()
    serializer_class = BreedSerializer

@extend_schema_view(
    get=extend_schema(
        summary='Cat list',
            description='Returns the list of all existing cats.',
            request=CatSerializer,
            responses={
                200: CatSerializer,
                204: OpenApiResponse(description='There are no cats yet.')
            },
            examples=[
                OpenApiExample(
                    name='/api/cats/breed/',
                    value={
                        'id': 1,
                        'name': 'Chuck',
                        'age': 31,
                        'color': 'black',
                        'description': 'hell of a cat',
                        'breed': 'scottish fold',
                        'owner': 'username'
                    }
                )
            ]
    )
)
class CatList(generics.ListAPIView):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer

    def list(self, request, *args, **kwargs):
        queryset = Cat.objects.all()

        if not queryset:
            return Response({'msg': 'There are no cats yet.'})
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema_view(
    get=extend_schema(
        summary='Cat list by breed',
        description='Returns the list of all cats with specified breed ID.',
        request=CatSerializer,
        responses={
            200: CatSerializer,
            404: OpenApiResponse(description='Cats with specified breed Id have not been found.')
        },
        examples=[
            OpenApiExample(
                name='/api/cats/breed/id',
                value={
                    'id': 1,
                    'name': 'Sam',
                    'age': 57,
                    'color': 'grey',
                    'description': 'hell of a cat',
                    'breed': 'scottish fold',
                    'owner': 'username'
                }
            )
        ]
    )
)
class CatListByBreed(generics.ListAPIView):
    serializer_class = CatSerializer

    def get_queryset(self):
        breed = get_object_or_404(Breed, id=self.kwargs['breed_id'])
        return Cat.objects.filter(breed=breed)


@extend_schema_view(
    post=extend_schema(
        summary='Create a cat',
        description='Creates a cat. To add a cat you need to pass name[str], age[int (in months)],'
        'color[str], breed[str], description[str] (optional).',
        request=CatSerializer,
        responses={
            201: CatSerializer
        },
        examples=[
            OpenApiExample(
                name='/api/cat/add/',
                value={
                    'id': 1,
                    'name': 'Sam',
                    'age': 57,
                    'color': 'grey',
                    'description': 'hell of a cat',
                    'breed': 'scottish fold',
                }
            )
        ]
    )
)   
class AddCat(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CatSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


@extend_schema_view(
    get=extend_schema(
        summary='Get details',
        description='Returns the details of the cat with specified ID.',
        request=CatSerializer,
        responses={
            200: CatSerializer,
            404: OpenApiResponse(description='Cat with specified ID has not been found.')
        }
    ),
    put=extend_schema(
        summary='Update details',
        description='Changes the details of the cat with specified ID.',
        request=CatSerializer,
        responses={
            200: CatSerializer
        }
    ),
    delete=extend_schema(
        summary='Delete a cat',
        description='Removes the cat with specified ID from the database.',
        request=CatSerializer,
        responses={
            200: OpenApiResponse('The cat has been successfully removed.'),    
        }
    )
)
class CatDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cat.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = CatSerializer
    
    def update(self, request, *args, **kwargs):
        breed_name = request.data.get('breed')
        cat = self.get_object()

        if breed_name:
            breed, created = Breed.objects.get_or_create(name=breed_name)
            cat.breed = breed

        request_data = request.data.copy()
        request_data.pop('breed', None)

        serializer = self.get_serializer(cat, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

class Rate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RatingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

