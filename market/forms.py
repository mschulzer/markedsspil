from django import forms
from .models import Market, Trade, Trader
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from math import floor


class MarketForm(forms.ModelForm):
    class Meta:
        model = Market

        fields = ['product_name_singular', 'product_name_plural', 'initial_balance',
                  'max_rounds', 'endless', 'alpha', 'beta', 'theta', 'min_cost', 'max_cost']
        help_texts = {
            'product_name_singular': _("The name of the product being traded in singular form (e.g 'baguette')"),
            'product_name_plural': _("The name of the product being traded in plural form (e.g. 'baguettes')"),
            'initial_balance': _("How much money should the participants start out with?"),
            'alpha': _("How big should the demand for a trader's product be, if all traders set their price to 0?"),
            'beta': _("How much should the demand of a single trader's product be reduced, when she/he raises their unit price by one?"),
            'theta': _("How much should the demand of a single trader's product increase, when the market's average price goes up by one?"),
            'min_cost': _("What is the lowest production cost for one unit of the product?"),
            'max_cost': _("What is the highest production cost for one unit of the product?"),
            'max_rounds': _(f"How many rounds should be played before the game ends? Choose number between 1 and {Market.UPPER_LIMIT_ON_MAX_ROUNDS}"),
            'endless': _("The game should go on for an indefinite number of rounds"),
        }
        labels = {
            'product_name_singular': _('Product name (singular)'),
            'product_name_plural': _('Product name (plural)'),
            'initial_balance': _('Initial balance'),
            'alpha': _('Alpha'),
            'beta': _('Beta'),
            'theta': _('Theta'),
            'min_cost': _('Min. prod. cost'),
            'max_cost': _('Max. prod. cost'),
            'endless': _('Endless'),
            'max_rounds': _('Max rounds'),
        }
        widgets = {
            'initial_balance': forms.NumberInput(attrs={'step': 0.01, 'onchange': "setTwoNumberDecimal(this)"}),
            'min_cost': forms.NumberInput(attrs={'step': 0.01, 'onchange': "setTwoNumberDecimal(this)"}),
            'max_cost': forms.NumberInput(attrs={'step': 0.01, 'onchange': "setTwoNumberDecimal(this)"})
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

    def clean_max_rounds(self):
        """Form is invalid if max_rounds < 1"""
        max_rounds = self.cleaned_data['max_rounds']

        if not (max_rounds is None) and max_rounds < 1:
            raise forms.ValidationError('There must be at least 1 round')
        return max_rounds


class MarketUpdateForm(MarketForm):

    class Meta(MarketForm.Meta):
        # fields = ['product_name_singular',
        #           'product_name_plural', 'alpha', 'beta', 'theta']

        widgets = {
            'initial_balance': forms.NumberInput(attrs={'readonly': True}),
            'min_cost': forms.NumberInput(attrs={'readonly': True}),
            'max_cost': forms.NumberInput(attrs={'readonly': True}),
        }

    def clean(self):
        """ 
        Max numner of rounds can't be smaller than current round + 1 (when endless = False) 
        If market.round = 7, the market is already in its 8'th round, so 8 shold be the minimal 
        choice for a new maximal number of rounds.  
        """
        cleaned_data = super().clean()
        endless = cleaned_data.get("endless")
        max_rounds = cleaned_data.get("max_rounds")
        if self.instance.game_over():
            raise ValidationError(
                "You can't edit a market that has ended (game is over)")
        if not endless:
            if max_rounds:
                if max_rounds < self.instance.round + 1:
                    raise forms.ValidationError(
                        "Number of rounds can't be smaller than the current round of the market".format(
                            self.instance.round + 1)
                    )
        return cleaned_data


class TraderForm(forms.ModelForm):
    market_id = forms.CharField(max_length=16, label=_("Market ID"), help_text=_(
        'Enter the ID of the market you want to join.'))

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
            market = Market.objects.get(market_id=cleaned_market_id)
            if market.game_over():
                raise forms.ValidationError(
                    _('This market has has ended. No new traders can join.'))

            elif Trader.objects.filter(name=cleaned_name, market=market).exists():
                raise forms.ValidationError(
                    _('There is already a trader with this name on the requested market. Please select another name'))

        return cleaned_data


class TradeForm(forms.ModelForm):
    class Meta:
        model = Trade
        fields = ('unit_price', 'unit_amount')
        widgets = {
            'unit_price': forms.NumberInput(attrs={'type': 'range', 'min': 0, 'class': 'slider', 'step': 0.1}),
            'unit_amount': forms.NumberInput(attrs={'type': 'range', 'min': 0, 'class': 'slider', 'step': 1}),
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

            self.fields['unit_price'].help_text = (_("Set a price for one {0} (your cost pr. {0} is <b>{1}</b> kr.)")).format(
                trader.market.product_name_singular, trader.prod_cost)
            self.fields['unit_amount'].help_text = (
                _("How many {0} do you want to produce?")).format(trader.market.product_name_plural)

            # Set default value of price slider equal to the trader's prod cost
            self.fields['unit_price'].widget.attrs['value'] = trader.prod_cost

            # Set default value of amount slider equal to zero
            self.fields['unit_amount'].widget.attrs['value'] = 0
