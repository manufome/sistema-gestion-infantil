from django import forms
from .models import Student
from institutions.models import Institution


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['registro', 'nombre', 'fecha_nacimiento', 'tipo_sangre', 'ciudad_nacimiento', 'guardian', 'telefono', 'direccion', 'eps', 'institution']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['institution'].queryset = Institution.get_aprobados()