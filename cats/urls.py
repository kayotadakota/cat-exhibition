from django.urls import path

from . import views


urlpatterns = [
    path('user/register/', views.RegisterUser.as_view(), name='user-register'),
    path('users/', views.UserList.as_view(), name='user-list'),
    path('breeds/', views.BreedList.as_view(), name='breed-list'),
    path('cats/', views.CatList.as_view(), name='cat-list'),
    path('cats/breed/<int:breed_id>', views.CatListByBreed.as_view(), name='cat-list-by-breed'),
    path('cat/details/<int:pk>', views.CatDetails.as_view(), name='cat-details'),
    path('cat/add/', views.AddCat.as_view(), name='add-cat'),
    path('cat/rate/', views.Rate.as_view(), name='rate-cat'),
]