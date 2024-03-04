from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from datetime import datetime
import json

timeseries_default = {"date": [], "value": []}

# Create your models here.
class CustomUser(AbstractUser):
    money = models.DecimalField(max_digits=100, decimal_places=2, validators=[MinValueValidator(50)])
    portfolio_graph = models.TextField(default=json.dumps(timeseries_default))
    portfolio_value = models.DecimalField(max_digits=100, decimal_places=2)
    portfolio_dict = models.JSONField(default=dict)

class Coin(models.Model):
    id = models.CharField(primary_key=True, max_length = 32)
    symbol = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)
    image_url = models.CharField(max_length=256)
    price = models.DecimalField(max_digits=15,decimal_places=4)
    market_cap = models.DecimalField(max_digits=20,decimal_places=2)
    volume = models.IntegerField()
    high_24h = models.DecimalField(max_digits=20,decimal_places=2)
    low_24h = models.DecimalField(max_digits=20,decimal_places=2)
    change_24h = models.DecimalField(max_digits=20,decimal_places=2)
    percent_change_24h = models.DecimalField(max_digits=20,decimal_places=2)
    graph = models.TextField(default=json.dumps(timeseries_default))