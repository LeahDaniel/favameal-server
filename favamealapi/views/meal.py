"""View module for handling requests about meals"""
from django.core.exceptions import ValidationError
from django.http import HttpResponseServerError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from favamealapi.models import Meal, MealRating, Restaurant, FavoriteMeal
from favamealapi.views.restaurant import RestaurantSerializer
from django.contrib.auth.models import User


class MealSerializer(serializers.ModelSerializer):
    """JSON serializer for meals"""
    # ? Why are we using a restaurant serializer here?
    restaurant = RestaurantSerializer(many=False)

    class Meta:
        model = Meal
        fields = ('id', 'name', 'restaurant', 'fans',
                  'favorite', 'user_rating', 'average_rating')


class MealView(ViewSet):
    """ViewSet for handling meal requests"""

    def create(self, request):
        """Handle POST operations for meals

        Returns:
            Response -- JSON serialized meal instance
        """
        meal = Meal()
        meal.name = request.data["name"]
        meal.restaurant = Restaurant.objects.get(
            pk=request.data["restaurant_id"])

        try:
            meal.save()
            serializer = MealSerializer(
                meal, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single meal

        Returns:
            Response -- JSON serialized meal instance
        """
        try:
            meal = Meal.objects.get(pk=pk)
            user = User.objects.get(pk=request.auth.user.id)
            #!user rating setter
            meal.user_rating = user.id

            #! favorite boolean properties added based on current user's stars
            # Check to see if the user is in the fans list on the restaurant
            meal.favorite = user in meal.fans.all()

            # ? Why are we using a restaurant serializer and passing it a meal?
            serializer = MealSerializer(
                meal, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def list(self, request):
        """Handle GET requests to meals resource

        Returns:
            Response -- JSON serialized list of meals
        """
        meals = Meal.objects.all()
        user = User.objects.get(pk=request.auth.user.id)

        #! favorite boolean properties added based on current user's stars
        # Set the `favorite` property on every event
        for meal in meals:
            # Check to see if the user is in the fans list on the meal
            meal.favorite = user in meal.fans.all()
            #!user rating setter
            meal.user_rating = user.id

        serializer = MealSerializer(
            meals, many=True, context={'request': request})

        return Response(serializer.data)

    #! rate custom actions added
    @action(methods=['post'], detail=True)
    def rate(self, request, pk):
        """Post request for a user to sign up for an event"""

        user = User.objects.get(pk=request.auth.user.id)
        meal = Meal.objects.get(pk=pk)
        
        meal_rating = MealRating.objects.get(meal=meal, user=user)

        if meal_rating is None:
            MealRating.objects.create(
                user=user,
                meal=meal,
                rating=request.data["rating"]
            )
        
            return Response({'message': 'User rating added'}, status=status.HTTP_201_CREATED)
        

    @action(methods=['put'], detail=True)
    def rerate(self, request, pk):
        """Post request for a user to sign up for an event"""

        user = User.objects.get(pk=request.auth.user.id)
        meal = Meal.objects.get(pk=pk)
        
        meal_rating = MealRating.objects.get(meal=meal, user=user)
        meal_rating.rating = request.data["rating"]
        meal_rating.save()
        
        return Response({'message': 'User rating updated'}, status=status.HTTP_204_NO_CONTENT)

    #  POST and a DELETE request to /meals/3/star.
    #! star custom actions added

    @action(methods=['post'], detail=True)
    def star(self, request, pk):
        """Post request for a user to sign up for an event"""

        user = User.objects.get(pk=request.auth.user.id)
        meal = Meal.objects.get(pk=pk)
        meal.fans.add(user)
        return Response({'message': 'User favorite added'}, status=status.HTTP_201_CREATED)

    @action(methods=['delete'], detail=True)
    def unstar(self, request, pk):
        """Post request for a user to sign up for an event"""

        user = User.objects.get(pk=request.auth.user.id)
        meal = Meal.objects.get(pk=pk)
        meal.fans.remove(user)
        return Response({'message': 'User favorite deleted'}, status=status.HTTP_204_NO_CONTENT)
