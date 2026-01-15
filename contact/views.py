from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import ContactForm
from django.contrib.messages.views import SuccessMessageMixin  # Ajoutez cette ligne
from .forms import ContactForm

class ContactView(SuccessMessageMixin, FormView):
    template_name = 'contact/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('courses:home')  
    success_message = "Votre message a été envoyé avec succès !"


def form_valid(self, form):
        form.send_email()
        messages.success(self.request, 'Votre message a été envoyé avec succès !')
        return super().form_valid(form)