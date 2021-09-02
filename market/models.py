from django.db import models
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal
from random import randint as random_integer
from random import choice


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
    product_name_singular = models.CharField(max_length=16)
    product_name_plural = models.CharField(max_length=16)

    # w/ below settings, alpha, beta and theta has to be positive numbers <= 9999999999.9999
    # When specifying the validators here, forms will automatically not validate with user input exceeding the chosen limits
    alpha = models.DecimalField(
        max_digits=14,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0000'))])

    beta = models.DecimalField(max_digits=14, decimal_places=4,
                               validators=[MinValueValidator(Decimal('0.0000'))])

    theta = models.DecimalField(max_digits=14, decimal_places=4,
                                validators=[MinValueValidator(Decimal('0.0000'))])

    # w/ below settings, initial balance, min_cost and max_cost has to be <= 9999999999.99
    # min_cost and max_cost has to be positive
    initial_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2)

    min_cost = models.DecimalField(max_digits=14, decimal_places=2,
                                   validators=[MinValueValidator(Decimal('0.01'))])

    max_cost = models.DecimalField(max_digits=14, decimal_places=2,
                                   validators=[MinValueValidator(Decimal('0.01'))])

    round = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(
        get_user_model(), null=True, on_delete=models.SET_NULL)

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
    # w/ below settings a trader's production cost pr unit has to be a positive amount <= 9999999999.99
    prod_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    # w/ below settings a trader's balance has be numerically <= 9999999999.99
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        # There can only be one trader with a given name in a given market.
        # Specifying the constraint here to discover bugs in code during development
        # The constraint is also specified in forms.py
        constraints = [
            models.UniqueConstraint(
                fields=['market', 'name'], name='market_and_name_unique_together'),
        ]

   
    def save(self, *args, **kwargs):
        """
        Set productions cost before creating a new trader. 
        """

        # If we are saving a new trader object (not updating an existing trader)
        if not self.id:
            # If a specific production cost not is provided (say, when defining creating a new trader object in a test)
            if not self.prod_cost:
                if self.market.min_cost == self.market.max_cost:
                    # set traders production cost equal to this value
                    self.prod_cost = self.market.min_cost

                # If min_cost < max_cost
                else:
                    # use production cost algorithm to set production cost of trader
                    self.prod_cost_algoritm()

        super(Trader, self).save(*args, **kwargs)


    def prod_cost_algoritm(self):
        """ 
        Used when market.min_cost < market.max_cost to produce 
        semi-random production costs that cover the whole spectrum of 
        possible production costs 
        """

        # Get all unused production costs
        unused_costs = UnusedCosts.objects.filter(
            market=self.market)

        # If there are any unused costs,
        if len(unused_costs) > 0:
            # pick one at random
            rnd_unused_cost = choice(unused_costs)
            self.prod_cost = rnd_unused_cost.cost
            # then move it to the used costs
            UsedCosts(cost=self.prod_cost,
                      market=self.market).save()
            rnd_unused_cost.delete()

        # If there are no unused costs,
        else:
            # use the costs "between" each pair of used costs as new unused costs
            all_used_costs = UsedCosts.objects.filter(
                market=self.market).order_by('cost')
            for i in range(len(all_used_costs)-1):
                new_unused_cost = (all_used_costs[i].cost/2
                                   + all_used_costs[i+1].cost/2)
                UnusedCosts(cost=new_unused_cost,
                            market=self.market).save()
            # then pick one of the new unused costs for this trader
            rnd_unused_cost = choice(
                UnusedCosts.objects.filter(market=self.market))
            self.prod_cost = rnd_unused_cost.cost
            UsedCosts(cost=self.prod_cost,
                      market=self.market).save()
            rnd_unused_cost.delete()


    def __str__(self):
        return f"{self.name} [{self.market.market_id}] - ${self.balance}"

    def is_ready(self):
        " A trader is 'ready' if (s)he has decided on a trade in the current round"
        has_traded_this_round = Trade.objects.filter(
            trader=self, round=self.market.round, was_forced=False).count() == 1
        return has_traded_this_round


class Trade(models.Model):
    trader = models.ForeignKey(Trader, on_delete=models.CASCADE)

    # w/ below settings, the unit_price can't set bigger than 9999999999.99
    # unit price can be null because 'forced trades' have no unit_price
    unit_price = models.DecimalField(
        null=True,
        max_digits=12,
        decimal_places=2,
    )
    # unit_amount is the number of products produced
    # unit_amount can be null, because 'forced trades' have no unit_amount
    unit_amount = models.IntegerField(null=True)

    round = models.IntegerField()  # not always equal to trader.market.round
    # a trade 'was-forced' if the trader did not make a trade decision in the given round.
    was_forced = models.BooleanField(default=False)

    # demand, units_sold, profit and balance_after will all be set to null when a trade object is created and
    # updated with a real value when the round is finished
    demand = models.IntegerField(null=True)

    units_sold = models.IntegerField(null=True)

    profit = models.DecimalField(
        null=True,
        max_digits=12,
        decimal_places=2,
    )
    balance_after = models.DecimalField(
        null=True,
        max_digits=12,
        decimal_places=2,
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        # There can only be one trade pr trader pr round
        # Specifying the constraint here to discover bugs in code during development
        constraints = [
            models.UniqueConstraint(
                fields=['trader', 'round'], name='trader_and_round_unique_together'),
        ]

    def __str__(self):
        return f"{self.trader.name} ${self.unit_price} x {self.unit_amount} [{self.trader.market.market_id}][{self.round}]"


class RoundStat(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    round = models.IntegerField()
    # w/ below settings avg. price can't be bigger than 9999999999.99
    avg_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        # There can only be one stat object pr market pr round
        # Specifying the constraint here to discover bugs in code during development

        constraints = [
            models.UniqueConstraint(
                fields=['market', 'round'], name='market_and_round_unique_together'),
        ]

    def __str__(self):
        return f"{self.market.market_id}[{self.round}]"


class UnusedCosts(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    cost = models.DecimalField(max_digits=14, decimal_places=2,
                               validators=[MinValueValidator(Decimal('0.01'))])

    class Meta:
        # There cannot be unused costs of the same value in the same market
        constraints = [
            models.UniqueConstraint(
                fields=['market', 'cost'], name='market_and_unused_cost_unique_together'),
        ]

    def __str__(self):
        return f"{self.cost}"


class UsedCosts(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    cost = models.DecimalField(max_digits=14, decimal_places=2,
                               validators=[MinValueValidator(Decimal('0.01'))])

    class Meta:
        # There cannot be used costs of the same value in the same market
        constraints = [
            models.UniqueConstraint(
                fields=['market', 'cost'], name='market_and_used_cost_unique_together'),
        ]

    def __str__(self):
        return f"{self.cost}"
