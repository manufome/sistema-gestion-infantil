from django import forms
from .models import Institution

class InstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = ['nombre', 'estado', 'direccion']
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 2}),
        }
