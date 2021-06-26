from django.db import models
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

def new_unique_market_id():
    """
    Create a new unique market ID (8 alphabetic chars)
    """
    while True:
        market_id = get_random_string(
            8, allowed_chars='ABCDEFGHIJKLMSOPQRSTUVXYZ')
        if not Market.objects.filter(market_id=market_id).exists():
            break
    return market_id

class Market(models.Model):
    market_id = models.CharField(max_length=16, primary_key=True)
    product_name_singular = models.CharField(default="default_singular",max_length=16,
        help_text="The singular form of the product being sold (e.g. 'baguette')")
    product_name_plural = models.CharField(default="default_plural", max_length=16,
        help_text="The plural form of the product being sold (eg. 'baguettes')")
    
    # w/ below settings, alpha, beta and theta can't exceed 
    initial_balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="How much money should the participants start out with?")

    alpha = models.DecimalField(
        max_digits=14, 
        decimal_places=4, 
        validators=[MinValueValidator(Decimal('0.0000'))],
        help_text="How big should the demand for a trader's product be, if all traders set the price to zero?"
    )

    beta = models.DecimalField(max_digits=14, decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.0000'))],
        help_text="How much should the demand for a trader's product decrease, when (s)he raises the unit price by one?")
    theta = models.DecimalField(max_digits=14, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.0000'))],
        help_text="How much should the demand for a trader's product increase, when the market's average price goes up by one?")
    min_cost = models.DecimalField(max_digits=14, decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="What are the minimal production costs for one unit of the product?"
        )
    max_cost = models.DecimalField(max_digits=14, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="What are the maximal production costs for one unit of the product?")
    round = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        """
        Set unique custom id for market before creating a new market object (not when updating an existing market)
        """
        if not self.market_id:
            self.market_id = new_unique_market_id()
        super(Market, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.market_id}[{self.round}]:{self.alpha},{self.beta},{self.theta}"

class Trader(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    name = models.CharField(max_length=16,)
    prod_cost = models.DecimalField(
        default=1,
        max_digits=14, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    balance = models.DecimalField(
        blank=True,
        max_digits=14,
        decimal_places=2,
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['market', 'name'], name='market_and_name_unique_together'),
        ]
    
    def __str__(self):
        return f"{self.name} [{self.market.market_id}] - ${self.balance}"

    def is_ready(self):
        has_traded_this_round = Trade.objects.filter(trader=self, round=self.market.round, was_forced=False).count() == 1     
        return has_traded_this_round

class Trade(models.Model):
    trader = models.ForeignKey(Trader, on_delete=models.CASCADE)
    unit_price = models.DecimalField(
        default=0,
        null=True,
        max_digits=14,
        decimal_places=2,
    )
    unit_amount = models.IntegerField(default=0, null=True)
    round = models.IntegerField() # not always equal to trader.market.round
    was_forced = models.BooleanField(default=False) 
    demand = models.IntegerField(null=True, blank=True)
    units_sold = models.IntegerField(null=True, blank=True) 
    profit = models.DecimalField(
        null=True,
        blank=True,
        max_digits=14,
        decimal_places=2,
    )
    balance_after = models.IntegerField(null=True, blank=True)
    models.DecimalField(
        null=True,
        blank=True,
        max_digits=14,
        decimal_places=2,
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['trader', 'round'], name='trader_and_round_unique_together'),
    ]
  
    def __str__(self):
        return f"{self.trader.name} ${self.unit_price} x {self.unit_amount} [{self.trader.market.market_id}][{self.round}]"

   
class RoundStat(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    round = models.IntegerField()  
    # w/ below settings avg. can't be bigger than 999999.9999.  
    # Therefore, there has to be an upper bound on choice of unit_price set by players. 
    avg_price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['market', 'round'], name='market_and_round_unique_together'),
        ]

    def __str__(self):
        return f"{self.market.market_id}[{self.round}]"
