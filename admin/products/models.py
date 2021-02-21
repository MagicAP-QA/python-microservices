# from django.db import models
from djongo import models
class Product(models.Model):
    _id = models.ObjectIdField()
    title = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    likes = models.PositiveIntegerField(default=0)


class User(models.Model):
    pass
