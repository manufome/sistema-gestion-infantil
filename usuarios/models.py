from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Usuario(AbstractUser):

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def is_administrador(self):
        return self.groups.filter(name='Administrador').exists()

    def is_madre_comunitaria(self):
        return self.groups.filter(name='Madre Comunitaria').exists()

    def is_acudiente(self):
        return self.groups.filter(name='Acudiente').exists()

    def get_roles(self):
        return self.groups.all()

    def get_role(self):
        return self.groups.all()[0]

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)


class Actividad(models.Model):
    TIPOS_ACTIVIDAD = (
        ('creacion', 'Creación'),
        ('actualizacion', 'Actualización'),
        ('eliminacion', 'Eliminación'),
        ('otro', 'Otro'),
    )

    tipo = models.CharField(max_length=20, choices=TIPOS_ACTIVIDAD)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()
    icono = models.CharField(max_length=50, default='fa-info-circle')
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-fecha']
