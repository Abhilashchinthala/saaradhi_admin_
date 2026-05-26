from django import forms
from .models import GlobalConfiguration

class GlobalConfigurationForm(forms.ModelForm):
    class Meta:
        model = GlobalConfiguration
        fields = ['base_fare', 'surge_multiplier', 'surge_cap', 'per_km_rate', 'per_min_rate']

    def clean_base_fare(self):
        val = self.cleaned_data.get('base_fare')
        if val is None or val < 0:
            raise forms.ValidationError("Base fare cannot be negative.")
        return val

    def clean_surge_multiplier(self):
        val = self.cleaned_data.get('surge_multiplier')
        if val is None or val < 1.0:
            raise forms.ValidationError("Surge multiplier cannot be less than 1.0.")
        return val

    def clean_surge_cap(self):
        val = self.cleaned_data.get('surge_cap')
        if val is None or val < 1.0:
            raise forms.ValidationError("Surge cap cannot be less than 1.0.")
        return val

    def clean_per_km_rate(self):
        val = self.cleaned_data.get('per_km_rate')
        if val is None or val < 0:
            raise forms.ValidationError("Per km rate cannot be negative.")
        return val

    def clean_per_min_rate(self):
        val = self.cleaned_data.get('per_min_rate')
        if val is None or val < 0:
            raise forms.ValidationError("Per min rate cannot be negative.")
        return val
