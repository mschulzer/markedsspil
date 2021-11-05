from django import forms
from .models import Market, Trade, Trader
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from math import floor


class MarketForm(forms.ModelForm):
    class Meta:
        model = Market

        fields = ['initial_balance', 'min_cost', 'max_cost', 'cost_slope', 'max_rounds', 'endless',
                  'alpha', 'theta', 'gamma', 'product_name_singular', 'product_name_plural', 'allow_robots']
        help_texts = {
            'product_name_singular': "Navnet på produktet i ental (f.eks. 'baguette')",
            'product_name_plural': "Navnet på produktet i flertal (f.eks. 'baguetter')",
            'initial_balance': "Hvor mange penge skal deltagerne starte med?",
            # alpha = grundlæggende efterspørgsel
            'alpha': "Hvor stor er efterspørgslen på producentens vare, hvis både producentens egen salgspris og gennemsnitsprisen på markedet er 0 kr.?",
            # theta = konkurrenceforhold
            'theta': "Hvor meget øges efterspørgslen på producentens vare, hvis gennemsnitsprisen stiger med 1 kr., mens producentens egen salgspris forbliver uændret?",
            # gamma = prisfølsomhed
            'gamma': "Hvor meget falder efterspørgslen på producentens vare, hvis både producentens egen salgspris og gennemsnitsprisen på markedet stiger med 1 kr.?",
            'min_cost': "Hvad er den laveste produktionsomkostning pr. enhed en producent kan tildeles?",
            'max_cost': "Hvad er den højeste produktionsomkostning pr. enhed en producent kan tildeles?",
            'cost_slope': "Beløbet, du vælger her, vil blive lagt til producentens omkostning pr. enhed ved afslutningen af hver runde (indtil du ændrer værdien)",
            'max_rounds': f"Hvor mange runder skal der spilles? Vælg et tal mellem 1 og {Market.UPPER_LIMIT_ON_MAX_ROUNDS}",
            'endless': "Der skal ikke være et loft over antal runder (spillet skal bare fortætte, så længe du ønsker det)",
            'allow_robots': "Producenterne skal kunne agere via algoritmer skrevet i Python"
        }
        labels = {
            'product_name_singular': 'Produktnavn (ental)',
            'product_name_plural': 'Produktnavn (flertal)',
            'initial_balance': 'Startsaldo',
            'alpha': 'Grundlæggende efterspørgsel',
            'theta': 'Konkurrenceforhold',
            'gamma': 'Prisfølsomhed',
            'min_cost': 'Minimal omkostning pr. enhed',
            'max_cost': 'Maksimal omkostning pr. enhed',
            'cost_slope': 'Ændring i produktionsomkostning pr. runde',
            'endless': 'Uendeligt spil',
            'max_rounds': 'Antal runder',
            'allow_robots': 'Tillad robotspillere'
        }
        widgets = {
            'initial_balance': forms.NumberInput(attrs={'step': 0.01, 'onchange': "setTwoNumberDecimal(this)"}),
            'min_cost': forms.NumberInput(attrs={'step': 0.01, 'onchange': "setTwoNumberDecimal(this)"}),
            'max_cost': forms.NumberInput(attrs={'step': 0.01, 'onchange': "setTwoNumberDecimal(this)"})
        }

    def clean(self):
        """ 
        Form validation that depends on more than one input value. 
        Error message will be shown on top of the form. 
        """
        # min cost < max cost
        cleaned_data = super().clean()
        min_cost = cleaned_data.get("min_cost")
        max_cost = cleaned_data.get("max_cost")
        if min_cost and max_cost:
            if min_cost > max_cost:
                raise ValidationError(
                    "Max cost must be bigger than min cost")

        return cleaned_data

    def clean_max_rounds(self):
        """Form is invalid if max_rounds < 1"""
        max_rounds = self.cleaned_data['max_rounds']

        if not (max_rounds is None) and max_rounds < 1:
            raise forms.ValidationError('There must be at least 1 round')
        return max_rounds


class MarketUpdateForm(MarketForm):

    class Meta(MarketForm.Meta):

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
        if self.instance.game_over:
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
            if market.game_over:
                raise forms.ValidationError(
                    _('This market has has ended. No new traders can join.'))

            elif Trader.objects.filter(name=cleaned_name, market=market).exists():
                raise forms.ValidationError(
                    _('A trader with this name has already joined this market. Please select another name'))

        return cleaned_data


class TradeForm(forms.ModelForm):
    auto_play = forms.BooleanField(
        widget=forms.HiddenInput(), required=False, initial=False)

    class Meta:
        model = Trade
        fields = ('unit_price', 'unit_amount')
        widgets = {
            'unit_price': forms.NumberInput(attrs={'type': 'text', 'class': 'price-slider'}),
            'unit_amount': forms.NumberInput(attrs={'type': 'text', 'class': 'production-slider'}),
        }

    def __init__(self, trader=None, market_average=None, *args, **kwargs):
        super(TradeForm, self).__init__(*args, **kwargs)

        if trader:
            # traders can set the price of a product up to 4 times market's maximal prod cost
            self.fields['unit_price'].widget.attrs['min'] = 0
            self.fields['unit_price'].widget.attrs['max'] = trader.market.max_allowed_price(
            )

            # make sure, that the trader can't choose to produce an amount of units, he can't afford
            if trader.prod_cost > 0:
                max_unit_amount = floor((trader.balance/trader.prod_cost))
            else:  # if prod_cost is 0 (this is currently not allowed to happen)
                max_unit_amount = 10000  # this number is arbitrary
            self.fields['unit_amount'].widget.attrs['min'] = 0
            self.fields['unit_amount'].widget.attrs['max'] = max_unit_amount

            # Only show market average after round 0
            if trader.market.round > 0 and market_average is not None:
                self.fields['unit_price'].widget.attrs['marketavg'] = market_average

            # Labels
            self.fields['unit_price'].label = (
                _("Set your price for one {0}")).format(trader.market.product_name_singular)

            self.fields['unit_amount'].label = (
                _("How many {0} do you want to produce?")).format(trader.market.product_name_plural)

            # Set default value of price slider equal to the trader's prod cost
            self.fields['unit_price'].widget.attrs['value'] = trader.prod_cost

            # Set default value of amount slider equal to zero
            self.fields['unit_amount'].widget.attrs['value'] = 0
