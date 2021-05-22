from django import forms
from .models import Market, Trader
from django.core.exceptions import ValidationError

class MarketForm(forms.ModelForm):
    class Meta:
        model = Market
        fields = ['alpha', 'beta', 'theta', 'min_cost', 'max_cost']
    
    def clean(self):
        """ Additional validation of form data """
        cleaned_data = super().clean()
        min_cost = cleaned_data.get("min_cost")
        max_cost = cleaned_data.get("max_cost")
        if min_cost and max_cost:
            if min_cost > max_cost:
                raise ValidationError("Min cost can't be bigger than max cost")
        return cleaned_data
    
class TraderForm(forms.Form):
    username = forms.CharField(max_length=16)
    market_id = forms.CharField(max_length=16) 

    def clean_market_id(self):
        """ Additional validation of the form's market_id field """
        market_id = self.cleaned_data['market_id']
        if not Market.objects.filter(pk=market_id).exists():
            raise forms.ValidationError('There is no market with this ID')
        return market_id

