from django import forms
from .models import OrderProduct, Order


class OrderProductForm(forms.ModelForm):
    class Meta:
        model = OrderProduct
        fields = ['product', 'amount']
        widgets = {'product': forms.HiddenInput()}


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order