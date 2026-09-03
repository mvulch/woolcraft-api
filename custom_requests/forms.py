from django import forms
from django.core.files.uploadedfile import UploadedFile

from .models import CustomRequest, CustomRequestMessage
from decimal import Decimal

MAX_IMAGE_SIZE =  5*1024*1024
ALLOWED_IMAGE_TYPES = ('image/jpeg','image/png','image/webp')

def validate_client_images(image):
    # if empty
    if not image:
        return image

    if isinstance(image, UploadedFile):
        if image.size > MAX_IMAGE_SIZE:
            raise forms.ValidationError(f'Твърде голям файл. Максимален размер: {MAX_IMAGE_SIZE // (1024 * 1024)} MB.')

    content_type = getattr(image, 'content_type', None)
    if content_type is None:
        return image
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise forms.ValidationError('Непозволен формат. Изберете изображение във формат PNG, JPEG или WebP.')
    return image

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
    def clean_reference_image(self):
        return validate_client_images(self.cleaned_data.get('reference_image'))

class CustomRequestMessageForm(forms.ModelForm):
    class Meta:
        model = CustomRequestMessage
        fields = ['text']
        labels = {'text': 'Съобщение'}

class OfferPriceForm(forms.Form):
    offered_price = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        min_value=Decimal('0.01'),
        max_value=Decimal('9999.99'),
        label='Предложена цена',
        error_messages={
            'invalid': 'Въведете валидна цена.',
            'min_value': 'Цената трябва да е положително число.',
            'max_value': 'Цената надвишава максималната допустима стойност.',
        }
    )