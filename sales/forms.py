from django import forms
from .models import SalesOffer, SalesOfferItem, Customer
from products.models import Product

class SalesOfferForm(forms.ModelForm):
    class Meta:
        model = SalesOffer
        fields = [
            'customer', 'project_name', 'currency', 'language', 'description',
            'company_name', 'company_address', 'company_tax_office', 'company_tax_number',
            'offer_date', 'delivery_place', 'delivery_date', 'validity_date', 'advance_payment',
            'terms', 'notes', 'payment_method',
            'bank_recipient', 'bank_name', 'bank_branch', 'bank_iban', 'bank_swift'
        ]
        widgets = {
            'customer': forms.Select(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5', 'placeholder': 'Müşteri Seçiniz'}),
            'project_name': forms.TextInput(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5', 'placeholder': 'Proje Adı (Zorunlu Değil)'}),
            'currency': forms.Select(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5'}),
            'language': forms.Select(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5'}),
            'description': forms.Textarea(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5', 'rows': 3, 'placeholder': 'Açıklama (Opsiyonel)'}),
            
            # Text Inputs
            'company_name': forms.TextInput(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5'}),
            'company_tax_office': forms.TextInput(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5'}),
            'company_tax_number': forms.TextInput(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5'}),
            'offer_date': forms.DateInput(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5', 'type': 'date'}),
            'delivery_place': forms.TextInput(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5'}),
            'delivery_date': forms.DateInput(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5', 'type': 'date'}),
            'validity_date': forms.DateInput(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5', 'type': 'date'}),
            'advance_payment': forms.TextInput(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5'}),
            'bank_recipient': forms.TextInput(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5'}),
            'bank_name': forms.TextInput(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5'}),
            'bank_branch': forms.TextInput(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5'}),
            'bank_iban': forms.TextInput(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5'}),
            'bank_swift': forms.TextInput(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5'}),
            'payment_method': forms.TextInput(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5'}),
            
            # TextAreas
            'company_address': forms.Textarea(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5', 'rows': 2}),
            'terms': forms.Textarea(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5', 'rows': 2}),
        }

class SalesOfferItemForm(forms.ModelForm):
    item_type = forms.ChoiceField(
        choices=[('PRODUCT', 'Ürün'), ('SUBPART', 'Alt Parça')],
        widget=forms.Select(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5 item-type-select'}),
        label="Tip",
        initial='PRODUCT'
    )

    class Meta:
        model = SalesOfferItem
        fields = ['item_type', 'product', 'subpart', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5 product-select'}),
            'subpart': forms.Select(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5 subpart-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5 quantity-input', 'step': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5 price-input', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.subpart:
                self.fields['item_type'].initial = 'SUBPART'
            else:
                self.fields['item_type'].initial = 'PRODUCT'

    def clean(self):
        cleaned_data = super().clean()
        item_type = cleaned_data.get('item_type')
        product = cleaned_data.get('product')
        subpart = cleaned_data.get('subpart')

        if item_type == 'PRODUCT' and not product:
             self.add_error('product', 'Ürün seçmelisiniz.')
        if item_type == 'SUBPART' and not subpart:
             self.add_error('subpart', 'Alt parça seçmelisiniz.')
        
        # Clear the other field to avoid ambiguity
        if item_type == 'PRODUCT':
            cleaned_data['subpart'] = None
        elif item_type == 'SUBPART':
            cleaned_data['product'] = None
            
        return cleaned_data

SalesOfferItemFormSet = forms.inlineformset_factory(
    SalesOffer, SalesOfferItem, form=SalesOfferItemForm,
    extra=1, can_delete=True
)

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'address', 'phone', 'email', 'tax_number', 'country']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5', 'placeholder': 'Firma Adı veya Ad Soyad'}),
            'address': forms.Textarea(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5'}),
            'email': forms.EmailInput(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5'}),
            'tax_number': forms.TextInput(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5'}),
            'country': forms.TextInput(attrs={'class': 'w-full bg-gray-100 border border-gray-400 text-gray-900 text-sm rounded focus:ring-blue-500 focus:border-blue-500 block p-2.5'}),
        }
