from django import forms
from .models import PurchaseMaster

class PurchaseMasterAdminForm(forms.ModelForm):
    class Meta:
        model = PurchaseMaster
        fields = '__all__'  # Include all model fields
        widgets = {
            'quantityPurchased': forms.NumberInput(attrs={'min': 1}),
            'purchasePrice': forms.NumberInput(attrs={'step': 0.01}),
        }

    def clean_quantityPurchased(self):
        quantity = self.cleaned_data.get('quantityPurchased')
        if quantity <= 0:
            raise forms.ValidationError("Quantity purchased must be greater than zero.")
        return quantity

    def clean_purchasePrice(self):
        price = self.cleaned_data.get('purchasePrice')
        if price <= 0:
            raise forms.ValidationError("Purchase price must be greater than zero.")
        return price

