from django import forms
from django.forms import ModelForm
from gestion_patient.models import Demande


class DemandeForm(ModelForm):
    class Meta:
        model = Demande
        fields = ['prenom', 'nom', 'ipp', 'degre_urgence','type_examen']
        widgets = {
       'degre_urgence':forms.Select,
       'type_examen':forms.Select
        }
        