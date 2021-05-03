from django.db import models

class Market(models.Model):
    market_id = models.CharField(max_length=16, primary_key=True)
    alpha = models.DecimalField(max_digits=10, decimal_places=4)
    theta = models.DecimalField(max_digits=10, decimal_places=4)
    beta  = models.DecimalField(max_digits=10, decimal_places=4)
    min_cost = models.IntegerField()
    max_cost = models.IntegerField()
    round = models.IntegerField(default=0)

    def __str__(self):
        return str(self.market_id) + " ["+str(self.round)+"]: " + str(self.alpha) + ", " + str(self.beta) + ", " + str(self.theta)

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

