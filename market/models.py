from django.db import models
from random import randint
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError


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
        if not self.market_id:
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
    prod_cost = models.IntegerField(default=0)
    initial_balance = 5000
    balance = models.IntegerField(default=initial_balance, blank=True) # not really used anywhere.
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return f"{self.name} [{self.market.market_id}] - ${self.balance}"

    def is_ready(self):
        #ikke testet
        if(Trade.objects.filter(trader=self,market=self.market, round=self.market.round).count() == 1):
            return True
        else:
            return False

class Trade(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE, blank=True)
    trader = models.ForeignKey(Trader, on_delete=models.CASCADE)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_amount = models.IntegerField(default=0)
    round = models.IntegerField(blank=True)
    was_forced = models.BooleanField(default=False) 
    profit = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    balance_after = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            if self.round:
                raise Exception("Don't specify a round when creating a trade (round is inferred from market)")         
            try:
                self.market
            except:            
                self.market = self.trader.market
                self.round = self.market.round
            else:  
                raise Exception("Don't specify a market when creating a trade (market is inferred from trader")
        return super(Trade, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.trader.name} ${self.unit_price} x {self.unit_amount} [{self.market.market_id}]"


