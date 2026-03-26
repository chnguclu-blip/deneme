from django import forms
from .models import Supplier, PurchaseProcess, PurchaseRequest

class TailwindFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-accent focus:ring focus:ring-accent focus:ring-opacity-50',
                'placeholder': field.label
            })


class SupplierForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_name', 'phone', 'email', 'address']


class PurchaseProcessForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = PurchaseProcess
        fields = ['title', 'description', 'status']


class PurchaseRequestForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        fields = ['product_name', 'quantity', 'description', 'supplier', 'process', 'status']
