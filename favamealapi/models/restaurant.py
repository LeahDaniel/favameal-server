from django.db import models
from .favoriterestaurant import FavoriteRestaurant
from django.contrib.auth.models import User


class Restaurant(models.Model):

    name = models.CharField(max_length=55, unique=True)
    #? If unique is true, what happens when a user tries to add a duplicate
    #? restaurant name? Would we need error handling for that?
    address = models.CharField(max_length=255)
    #? Should I have added this many-to-many field? There wasn't a "to-do" telling me to
    fans = models.ManyToManyField(User, through=FavoriteRestaurant, related_name="favorited")
    
    #! favorite custom properties added
    @property
    def favorite(self):
        return self.__favorite

    @favorite.setter
    def favorite(self, value):
        self.__favorite = value
