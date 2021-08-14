from django import forms
from .models import Market, Trade, Trader
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from math import floor

class MarketForm(forms.ModelForm):
    class Meta:
        model = Market
        fields = ['product_name_singular', 'product_name_plural', 'initial_balance', 'alpha', 'beta', 'theta', 'min_cost', 'max_cost']
        help_texts = {
            'product_name_singular': _("The name of the product in singular form (e.g 'baguette')."),
            'product_name_plural': _("The name of the product in plural form (e.g. 'baguettes')."),
            'initial_balance': _("What balance should the traders start with?"),
            'alpha': _("How much should the product demand be if all traders set their price to 0?"),
            'beta': _("How much should the demand of a single trader's product be reduced if they increase their price per unit by 1?"),
            'theta': _("How much should the demand of a single trader's product be increased if the average market price increases by 1?"),
            'min_cost': _("What is the lowest production cost a trader can have?"),
            'max_cost': _("What is the highest production cost a trader can have?")
        }
        labels = {
            'product_name_singular': _('Product name (singular)'),
            'product_name_plural': _('Product name (plural)'),
            'initial_balance': _('Initial balance'),
            'alpha': _('Alpha'),
            'beta': _('Beta'),
            'theta': _('Theta'),
            'min_cost': _('Min. prod. cost'),
            'max_cost': _('Max. prod. cost')
        }

    def clean(self):
        """ Form is invalid if min cost > max cost """
        cleaned_data = super().clean()
        min_cost = cleaned_data.get("min_cost")
        max_cost = cleaned_data.get("max_cost")
        if min_cost and max_cost:
            if min_cost > max_cost:
                raise ValidationError("Min cost can't be bigger than max cost")
        return cleaned_data

    def clean_alpha(self):
        """ Form is invalid if alpha < 0 """
        alpha = self.cleaned_data['alpha']

        if alpha < 0:
            raise forms.ValidationError('Alpha should be non-negative for market to make sense')
        return alpha

    def clean_beta(self):
        """ Form is invalid if beta < 0 """
        beta = self.cleaned_data['beta']

        if beta < 0:
            raise forms.ValidationError('Beta should be non-negative for market to make sense')
        return beta

    def clean_theta(self):
        """ Form is invalid if beta < 0 """
        theta = self.cleaned_data['theta']

        if theta < 0:
            raise forms.ValidationError(
                'Theta should be non-negative for market to make sense')
        return theta

    def clean_min_cost(self):
        """ Mininimal production cost should be greater than 0 """
        min_cost = self.cleaned_data['min_cost']

        if min_cost <= 0:
            raise forms.ValidationError(
                'Min cost should be greater than 0')
        return min_cost


    def clean_max_cost(self):
        """ Maximal production cost should be greater than 0 """
        max_cost = self.cleaned_data['max_cost']

        if max_cost <= 0:
            raise forms.ValidationError(
                'Max cost should be greater than 0')
        return max_cost

class MarketUpdateForm(MarketForm):
    
    class Meta(MarketForm.Meta):
        fields = ['product_name_singular','product_name_plural', 'alpha', 'beta', 'theta']
 
class TraderForm(forms.ModelForm):
    market_id = forms.CharField(max_length=16, label=_("Market ID"), help_text=_('The ID of the market you want to join.'))

    class Meta:
        model = Trader
        fields = ['name']
        labels = {
            'name': _('Name'),
        }
        help_texts = {
            'name': _('The name you choose will be visible to other traders on the market.'),
        }

    def clean_market_id(self):
        """ Additional validation of the form's market_id field """
        market_id = self.cleaned_data['market_id'].upper()

        if not Market.objects.filter(pk=market_id).exists():
            raise forms.ValidationError(_('There is no market with this ID'))
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
                    _('There is already a trader with this name on the requested market. Please select another name'))
        return cleaned_data
        

class TradeForm(forms.ModelForm):
    class Meta:
        model = Trade
        fields = ('unit_price', 'unit_amount')
        widgets = {
            'unit_price': forms.NumberInput(attrs={'type': 'range', 'min':0, 'class':'slider', 'step':1}),
            'unit_amount': forms.NumberInput(attrs={'type': 'range', 'min':0, 'class':'slider', 'step':1}),
        }
        labels = {
            'unit_price': _('Price')+': ',
            'unit_amount': _('Amount')+': '
        }
        help_texts = {
            'unit_amount': ('How many units do you want to produce?'),
        }

    def __init__(self, trader=None, *args, **kwargs):
        super(TradeForm, self).__init__(*args, **kwargs)

        if trader:
            # traders can set the price of a product up to 5 times market's maximal prod cost
            self.fields['unit_price'].widget.attrs['max'] = 5 * \
                trader.market.max_cost

            # make sure, trader can't choose to produce an amount of units, he can't afford
            if trader.prod_cost > 0:
                max_unit_amount = floor((trader.balance/trader.prod_cost))
            else:  # if prod_cost is 0 (this is currently not allowed to happen) 
                max_unit_amount = 10000  # this number is arbitrary

            self.fields['unit_amount'].widget.attrs['max'] = max_unit_amount 
            self.fields['unit_price'].help_text = (_("Set a price for one {0} (your costs pr. {0} are {1} kr.)")).format(trader.market.product_name_singular,trader.prod_cost)
            self.fields['unit_amount'].help_text = (_("How many {0} do you want to produce?")).format(trader.market.product_name_plural)
