"""
Convenience script only used in development to import models into the django shell and define som variables. 

from easy import *
"""
from market.models import Market, Trader, Trade

# delete all markets, traders, and trades
Market.objects.all().delete()
Trader.objects.all().delete()
Trade.objects.all().delete()

market1 = Market.objects.create()
trader11 = Trader.objects.create(market=market1, name="trader11")
trader12 = Trader.objects.create(market=market1, name="trader12")
trade1 = Trade.objects.create(trader=trader11, round=0)
trade2 = Trade.objects.create(trader=trader12, round=1)


market2 = Market.objects.create()
trader21 = Trader.objects.create(market=market2, name="trader21")
trader22 = Trader.objects.create(market=market2, name="trader22")
trade3 = Trade.objects.create(trader=trader21, round=0)
trade4 = Trade.objects.create(trader=trader22, round=1)

# All traders in market 1
Trader.objects.filter(market=market1)

# All trades where the trader is in market 1 == all trades in market 1
#Trade.objects.filter(trader__in=Trader.objects.filter(market=market1)).distinct()
#Trade.objects.filter(trader__in=Trader.objects.filter(market=market1)).distinct()


#Trade.objects.filter(trader__in=Trader.objects.filter(market=market1)).filter(round=round)

#Article.objects.filter(reporter__pk=1)


# Delete alle markets
# Market.objects.all().delete()
