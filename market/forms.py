from django import forms
from .models import Market, Trade, Trader
from django.core.exceptions import ValidationError
from math import floor

class MarketForm(forms.ModelForm):
    class Meta:
        model = Market
        fields = ['alpha', 'beta', 'theta', 'min_cost', 'max_cost']
        help_texts = {
            'alpha': ("How big should the demand for a trader's product be, if all traders set the price to zero?"),
            'beta': ("How much should the demand for a trader's product decrease, when (s)he raises the unit price by one?"),
            'theta':("How much should the demand for a trader's product increase, when the market's average price goes up by one?"),
            'min_cost':("What is the minimal production cost for one unit of the product?"),
            'max_cost': ("What is the maximal production cost for one unit of the product?")
        }

    def clean(self):
        """ Additional validation of input data """
        cleaned_data = super().clean()
        min_cost = cleaned_data.get("min_cost")
        max_cost = cleaned_data.get("max_cost")
        if min_cost and max_cost:
            if min_cost > max_cost:
                raise ValidationError("Min cost can't be bigger than max cost")
        return cleaned_data
    
class TraderForm(forms.ModelForm):
    market_id = forms.CharField(max_length=16, label="Market ID", help_text='Enter the ID of the market you want to join') 

    class Meta:
        model = Trader
        fields = ['name']
        labels = {
            'name': ('Name'),
        }
        help_texts = {
            'name': ('The name you choose here will be visible in the scoreboard for the participant in this market'),
        }

    def clean_market_id(self):
        """ Additional validation of the form's market_id field """
        market_id = self.cleaned_data['market_id']

        if not Market.objects.filter(pk=market_id).exists():
            raise forms.ValidationError('There is no market with this ID')
        return market_id

    def clean(self):
        """ 
        Additional validation of form data: 
        Validate that there are no other users on the market with the chosen username
        """
        cleaned_data = super().clean()
        cleaned_name = cleaned_data.get("name")
        cleaned_market_id = cleaned_data.get('market_id')
        if cleaned_name and cleaned_market_id:
            market = Market.objects.get(market_id = cleaned_market_id)
            if Trader.objects.filter(name=cleaned_name, market=market).exists():
                raise forms.ValidationError(
                    'There is already a trader with this name on the requested market. Please select another name')
        return cleaned_data
        

class TradeForm(forms.ModelForm):
    class Meta:
        model = Trade
        fields = ['unit_price', 'unit_amount']
        widgets = {
            'unit_price': forms.NumberInput(attrs={'type': 'range', 'min':0, 'max':30, 'class':'slider', 'step':1}),
            'unit_amount': forms.NumberInput(attrs={'type': 'range', 'min': 0, 'class':'slider', 'step':1}),
        }
        labels = {
            'unit_price': ('Price: '),
            'unit_amount': ('Amount: ')
        }
        help_texts = {
            'unit_price': ('Select a price for one unit of your product'),
            'unit_amount': ('How many units do you want to produce?'),
        }

    def __init__(self, trader=None, *args, **kwargs):
        super(TradeForm, self).__init__(*args, **kwargs)

        if trader:
            if trader.prod_cost > 0:  
                max_unit_amount = floor((trader.balance/trader.prod_cost))
            else:  # should this even be allowed to happen?
                max_unit_amount = 100  # this number is arbitrary at this point

            self.fields['unit_amount'].widget.attrs['max'] = max_unit_amount #test this

