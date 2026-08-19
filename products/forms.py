from django import forms
from .models import ProductReview

class ProductReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i,i) for i in range(1,6)],
        label='Оценка'
    )
    class Meta:
        model = ProductReview
        fields = ['rating','comment']
        labels = {'comment': 'Коментар'}
