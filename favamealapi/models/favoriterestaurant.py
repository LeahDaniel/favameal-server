from django.contrib.auth.models import User
from django.db import models

#? Why are these related_names the same?
class FavoriteRestaurant(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="userfavoriterestaurants")
    restaurant = models.ForeignKey(
        "Restaurant", on_delete=models.CASCADE, related_name="userfavoriterestaurants")
