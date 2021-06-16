"""
Convenience script only used in local development to facilitate import of models and some pre-defined variables into the django shell. 
Usage: 
@ python mange.py shell
>>>from easy import*
"""
from market.models import Market, Trader, Trade, RoundStat

print("Imported Market, Trader and Trade models")

# delete all markets, traders, and trades
#Market.objects.all().delete()

market1 = Market.objects.create(round=1)
trader11 = Trader.objects.create(market=market1, name="trader11")
trader12 = Trader.objects.create(market=market1, name="trader12")
trade110 = Trade.objects.create(trader=trader11, round=0)
trade111 = Trade.objects.create(trader=trader11, round=1)
trade120 = Trade.objects.create(trader=trader12, round=0)
trade121 = Trade.objects.create(trader=trader12, round=1)

market2 = Market.objects.create(round=1)
trader21 = Trader.objects.create(market=market2, name="trader21")
trader22 = Trader.objects.create(market=market2, name="trader22")
trade210 = Trade.objects.create(trader=trader21, round=0)
trade211 = Trade.objects.create(trader=trader21, round=1)
trade220 = Trade.objects.create(trader=trader22, round=0)
trade221 = Trade.objects.create(trader=trader22, round=1)

print("Defined market1, trader11, trader12, market2, trader21, trader22 some trades")



# All traders in market 1
#Trader.objects.filter(market=market1)

# All trades where the trader is in market 1 == all trades in market 1
#Trade.objects.filter(trader__in=Trader.objects.filter(market=market1)).distinct()
#Trade.objects.filter(trader__in=Trader.objects.filter(market=market1)).distinct()


#Trade.objects.filter(trader__in=Trader.objects.filter(market=market1)).filter(round=round)

#Article.objects.filter(reporter__pk=1)


