"""View module for handling requests about restaurants"""
from django.core.exceptions import ValidationError
from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from django.contrib.auth.models import User
from favamealapi.models import Restaurant, FavoriteRestaurant


class RestaurantSerializer(serializers.ModelSerializer):
    """JSON serializer for restaurants"""

    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'address', 'fans', 'favorite')


class FaveSerializer(serializers.ModelSerializer):
    """JSON serializer for favorites"""

    class Meta:
        model = FavoriteRestaurant
        fields = ('restaurant',)
        depth = 1


class RestaurantView(ViewSet):
    """ViewSet for handling restuarant requests"""

    def create(self, request):
        """Handle POST operations for restaurants

        Returns:
            Response -- JSON serialized event instance
        """
        rest = Restaurant()
        rest.name = request.data["name"]
        rest.address = request.data["address"]

        try:
            rest.save()
            serializer = RestaurantSerializer(
                rest, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as ex:
            return Response({"reason": ex.message}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single event

        Returns:
            Response -- JSON serialized game instance
        """
        try:
            restaurant = Restaurant.objects.get(pk=pk)
            user = User.objects.get(pk=request.auth.user.id)

            #! favorite boolean properties added based on current user's stars
            # Check to see if the user is in the fans list on the restaurant
            restaurant.favorite = user in restaurant.fans.all()

            serializer = RestaurantSerializer(
                restaurant, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def list(self, request):
        """Handle GET requests to restaurants resource

        Returns:
            Response -- JSON serialized list of restaurants
        """
        restaurants = Restaurant.objects.all()
        user = User.objects.get(pk=request.auth.user.id)

        #! favorite boolean properties added based on current user's stars
        # Set the `favorite` property on every event
        for restaurant in restaurants:
            # Check to see if the user is in the fans list on the restaurant
            restaurant.favorite = user in restaurant.fans.all()

        serializer = RestaurantSerializer(
            restaurants, many=True, context={'request': request})

        return Response(serializer.data)

    #! star custom actions added
    @action(methods=['post'], detail=True)
    def star(self, request, pk):
        """Post request for a user to sign up for an event"""

        user = User.objects.get(pk=request.auth.user.id)
        restaurant = Restaurant.objects.get(pk=pk)
        restaurant.fans.add(user)
        return Response({'message': 'User favorite added'}, status=status.HTTP_201_CREATED)

    @action(methods=['delete'], detail=True)
    def unstar(self, request, pk):
        """Post request for a user to sign up for an event"""

        user = User.objects.get(pk=request.auth.user.id)
        restaurant = Restaurant.objects.get(pk=pk)
        restaurant.fans.remove(user)
        return Response({'message': 'User favorite deleted'}, status=status.HTTP_204_NO_CONTENT)
