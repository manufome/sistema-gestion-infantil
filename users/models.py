from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class User(AbstractUser):

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def is_administrador(self):
        return self.groups.filter(name='Administrator').exists()

    def is_teacher(self):
        return self.groups.filter(name='Teacher').exists()

    def is_guardian(self):
        return self.groups.filter(name='Guardian').exists()

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
