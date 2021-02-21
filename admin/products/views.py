from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product, User
from .producer import publish
from .serializers import ProductSerializer
import random

import redis
import json

redis_instance = redis.StrictRedis(host='localhost', port=6379, db=0)
class ProductViewSet(viewsets.ViewSet):
    def list(self, request=None, redis_cache=True):
        # if redis_cache:
        #     print("Fetching from redis")
        #     data = redis_instance.get("products_list")
        #     return Response(data)
        print("Fetching from database")
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)

        return Response(serializer.data)

    def create(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        publish('product_created', serializer.data)
        print("*"*30)
        # json_list = self.list(redis_cache=False)
        # print(f"json list -=== {json_list.data}")
        # redis_instance.set("products_list", json_list.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def update(self, request, pk=None):
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(instance=product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        publish('product_updated', serializer.data)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, pk=None):
        product = Product.objects.get(id=pk)
        product.delete()
        publish('product_deleted', pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserAPIView(APIView):
    def get(self, _):
        users = User.objects.all()
        user = random.choice(users)
        return Response({
            'id': user.id
        })
