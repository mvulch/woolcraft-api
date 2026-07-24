from django import forms
from .models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['first_name', 'last_name', 'phone', 'street', 'city', 'postal_code', 'country', 'address_type']
        widgets = {
            'address_type': forms.Select(attrs={'class': 'form-select '})
        }
        labels = {
            'first_name': 'Име',
            'last_name': 'Фамилия',
            'phone': 'Телефон',
            'street': 'Улица и номер',
            'city': 'Град',
            'postal_code': 'Пощенски код',
            'country': 'Държава',
            'address_type': 'Тип адрес',
        }