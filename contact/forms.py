from django import forms
from django.core.mail import send_mail
from django.conf import settings

class ContactForm(forms.Form):
    name = forms.CharField(label='Votre nom', max_length=100)
    email = forms.EmailField(label='Votre email')
    subject = forms.CharField(label='Sujet', max_length=100)
    message = forms.CharField(label='Message', widget=forms.Textarea)

    def send_email(self):
        subject = f"Contact: {self.cleaned_data['subject']}"
        message = f"De: {self.cleaned_data['name']} <{self.cleaned_data['email']}>\n\n{self.cleaned_data['message']}"
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            ['votre-email@example.com'],  # Remplacez par votre adresse email
            fail_silently=False,
        )