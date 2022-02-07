from django.db import models

from favamealapi.models.mealrating import MealRating
from .favoritemeal import FavoriteMeal
from django.contrib.auth.models import User


class Meal(models.Model):

    name = models.CharField(max_length=55)
    restaurant = models.ForeignKey("Restaurant", on_delete=models.CASCADE)
    fans = models.ManyToManyField(
        User, through=FavoriteMeal, related_name="favoritedMeal")

    #! favorite custom properties added
    @property
    def favorite(self):
        return self.__favorite

    @favorite.setter
    def favorite(self, value):
        self.__favorite = value

    #! average rating custom property added
    @property
    def average_rating(self):
        """Average rating calculated attribute for each meal"""
        ratings = MealRating.objects.filter(meal=self)

        # Sum all of the ratings for the meal
        total_rating = 0

        if len(ratings) > 0:
            for rating in ratings:
                total_rating += rating.rating

            return total_rating / len(ratings)
        else:
            return None

    #! user rating custom properties added
    @property
    def user_rating(self):
        return self.__user_rating

    @user_rating.setter
    def user_rating(self, user_id):
        """current user's rating for meal"""

        user = User.objects.get(pk=user_id)
        rating = MealRating.objects.get(user=user, meal=self)

        if rating:
            self.__user_rating = rating.rating
        else:
            self.__user_rating = 0
