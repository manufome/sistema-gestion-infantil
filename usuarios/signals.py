from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from usuarios.models import Usuario

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    groups = {
        'Administrador': {
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
        'Madre Comunitaria': {
            'niños.view_niño': 'Puede ver niño',
            'niños.add_asistencia': 'Puede añadir asistencia',
            'niños.change_asistencia': 'Puede modificar asistencia',
            'niños.delete_asistencia': 'Puede eliminar asistencia',
            'niños.view_asistencia': 'Puede ver asistencia',
            'niños.add_avance_academico': 'Puede añadir avance académico',
            'niños.view_avance_academico': 'Puede modificar avance académico',
            'niños.view_avance_academico': 'Puede ver avance académico',
        },
        'Acudiente': {
            'niños.view_niño': 'Puede ver niño',
            'niños.view_avance_academico': 'Puede ver avance académico',
            'publicaciones.view_publicacion': 'Puede ver publicación',
        },
    }

    for group_name, permissions in groups.items():
        try:
            group, created = Group.objects.get_or_create(name=group_name)
            for permission_codename, permission_name in permissions.items():
                try:
                    permission, created = Permission.objects.get_or_create(
                        codename=permission_codename,
                        name=permission_name,
                        content_type=ContentType.objects.get_for_model(Usuario)
                    )
                    group.permissions.add(permission)
                    print(f"Permiso '{permission_name}' añadido al grupo '{group_name}'.")
                except Exception as e:
                    print(f"Error al crear o añadir el permiso '{permission_name}' al grupo '{group_name}': {e}")
        except Exception as e:
            print(f"Error al crear o obtener el grupo '{group_name}': {e}")
            
