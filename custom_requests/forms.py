from django import forms
from .models import CustomRequest, CustomRequestMessage

class CustomRequestForm(forms.ModelForm):
    class Meta:
        model = CustomRequest
        fields = ['title', 'description', 'specific_colors', 'size','reference_image']
        labels = {
            'title': 'Заглавие',
            'description': 'Описание',
            'specific_colors': 'Конкретни желани цветове',
            'size': 'Ориентировъчен размер',
            'reference_image': 'Примерна снимка',
        }

class CustomRequestMessageForm(forms.ModelForm):
    class Meta:
        model = CustomRequestMessage
        fields = ['text']
        labels = {'text': 'Съобщение'}