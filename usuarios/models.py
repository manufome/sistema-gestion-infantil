from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver

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


@receiver(post_migrate)
def crear_grupos(sender, **kwargs):
    groups = {
        'Administrador': {
            'name': 'Administrador',
            'permissions': {
                'usuarios.add_usuario': 'Puede añadir usuario',
                'usuarios.change_usuario': 'Puede modificar usuario',
                'usuarios.delete_usuario': 'Puede eliminar usuario',
                'usuarios.view_usuario': 'Puede ver usuario',
                'jardines.add_jardin': 'Puede añadir jardín',
                'jardines.change_jardin': 'Puede modificar jardín',
                'jardines.delete_jardin': 'Puede eliminar jardín',
                'jardines.view_jardin': 'Puede ver jardín',
                'niños.add_niño': 'Puede añadir niño',
                'niños.change_niño': 'Puede modificar niño',
                'niños.delete_niño': 'Puede eliminar niño',
                'niños.view_niño': 'Puede ver niño',
                'niños.view_asistencia': 'Puede ver asistencia',
                'publicaciones.add_publicacion': 'Puede añadir publicación',
                'publicaciones.change_publicacion': 'Puede modificar publicación',
                'publicaciones.delete_publicacion': 'Puede eliminar publicación',
                'publicaciones.view_publicacion': 'Puede ver publicación',
            },
        },
        'Madre Comunitaria': {
            'name': 'Madre Comunitaria',
            'permissions': {
                'niños.view_niño': 'Puede ver niño',
                'niños.add_asistencia': 'Puede añadir asistencia',
                'niños.change_asistencia': 'Puede modificar asistencia',
                'niños.delete_asistencia': 'Puede eliminar asistencia',
                'niños.view_asistencia': 'Puede ver asistencia',
                'niños.avance_academico': 'Puede añadir avance académico',
                'niños.view_avance_academico': 'Puede modificar avance académico',
                'niños.view_avance_academico': 'Puede ver avance académico',
            },
        },
        'Acudiente': {
            'name': 'Acudiente',
            'permissions': {
                'niños.view_niño': 'Puede ver niño',
                'niños.avance_academico': 'Puede ver avance académico',
                'publicaciones.view_publicacion': 'Puede ver publicación',
            },
        },
    }

    for group_name, group_data in groups.items():
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            for permission_codename, permission_name in group_data['permissions'].items():
                app_label, model_action = permission_codename.split('.')
                try:
                    permission = Permission.objects.get(
                        codename=model_action,
                        content_type__app_label=app_label
                    )
                    group.permissions.add(permission)
                except Permission.DoesNotExist:
                    print(f"Permiso no encontrado: {permission_codename}")

    print("Grupos y permisos creados exitosamente")