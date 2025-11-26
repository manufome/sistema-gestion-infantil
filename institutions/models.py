from django.db import models

class Institution(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    direccion = models.TextField()
    estado = models.CharField(max_length=20, choices=[
        ('Aprobado', 'Aprobado'),
        ('En trámite', 'En trámite'),
        ('Negado', 'Negado')
    ])
    fecha_registro = models.DateField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.nombre

    @classmethod
    def get_aprobados(cls):
        return cls.objects.filter(estado='Aprobado')