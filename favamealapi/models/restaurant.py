from django.db import models
from .favoriterestaurant import FavoriteRestaurant
from django.contrib.auth.models import User


class Restaurant(models.Model):

    name = models.CharField(max_length=55, unique=True)
    #? If unique is true, what happens when a user tries to add a duplicate
    #? restaurant name? Would we need error handling for that?
    address = models.CharField(max_length=255)
    #! many to many field added
    fans = models.ManyToManyField(User, through=FavoriteRestaurant, related_name="favoritedRest")
    
    #! favorite custom properties added
    @property
    def favorite(self):
        return self.__favorite

    @favorite.setter
    def favorite(self, value):
        self.__favorite = value
