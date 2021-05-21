from django.db import models
from random import randint

class Market(models.Model):
    market_id = models.CharField(max_length=16, primary_key=True)
    alpha = models.DecimalField(max_digits=10, decimal_places=4, default=105)
    beta = models.DecimalField(max_digits=10, decimal_places=4, default=17.5)
    theta = models.DecimalField(max_digits=10, decimal_places=4, default=14.58)
    min_cost = models.IntegerField(default=5)
    max_cost = models.IntegerField(default=15)
    round = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        """ create unique 8 character market_id before saving instance """
        good_id = False
        market_id = ""
        while not good_id:
            for i in range(8):
                market_id += chr(randint(65, 90))
            if len(Market.objects.filter(market_id=market_id)) == 0:
                good_id = True
            else:
                market_id = ""
        self.market_id = market_id
        super(Market, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.market_id}[{self.round}]:{self.alpha},{self.beta},{self.theta}"

class Trader(models.Model):
    id = models.AutoField(primary_key=True)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    name = models.CharField(max_length=16)
    money = models.IntegerField(default=0)
    prod_cost = models.IntegerField(default=0)

    def __str__(self):
        return str(self.name) + " [" + str(self.market.market_id) + "] - " + "$" + str(self.money)

class Trade(models.Model):
    id = models.AutoField(primary_key=True)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    trader = models.ForeignKey(Trader, on_delete=models.CASCADE)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_amount = models.IntegerField(default=0)
    round = models.IntegerField(default=0)

    def __str__(self):
        return str(self.trader.name) + " $" + str(self.unit_price) + " x " + str(self.unit_amount) + " [" + str(self.market.market_id) + "]"

class Stats(models.Model):
    id = models.AutoField(primary_key=True)
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    trader = models.ForeignKey(Trader, on_delete=models.CASCADE)
    round = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=4)
    amount = models.DecimalField(max_digits=10, decimal_places=4)
    profit = models.DecimalField(max_digits=10, decimal_places=4)
    bank = models.IntegerField()

