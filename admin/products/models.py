from django.db import models

class Product(models.Model):
    # id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    likes = models.PositiveIntegerField(default=0)


class User(models.Model):
    pass
