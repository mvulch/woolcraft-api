from django import forms
from .models import ContactMessage, ContactMessageReply

class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['subject', 'text']
        labels = {
            'subject': 'Тема',
            'text': 'Съобщение',
        }

class ContactMessageReplyForm(forms.ModelForm):
    class Meta:
        model = ContactMessageReply
        fields = {'text'}
        labels = {'text': 'Съобщение',}
