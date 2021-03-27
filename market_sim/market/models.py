from django.db import models

class Market(models.Model):
    market_id = models.CharField(max_length = 16)
    alpha = models.DecimalField(max_digits = 10, decimal_places=4)
    theta = models.DecimalField(max_digits = 10, decimal_places=4)
    beta  = models.DecimalField(max_digits = 10, decimal_places=4)
    min_cost = models.IntegerField()
    max_cost = models.IntegerField()

class Trader(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    name = models.CharField(max_length = 16)
