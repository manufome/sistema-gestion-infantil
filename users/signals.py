from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from users.models import User

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    groups = {
        'Administrator': {
            'users.add_user': 'Can add user',
            'users.change_user': 'Can change user',
            'users.delete_user': 'Can delete user',
            'users.view_user': 'Can view user',
            'institutions.add_institution': 'Can add institution',
            'institutions.change_institution': 'Can change institution',
            'institutions.delete_institution': 'Can delete institution',
            'institutions.view_institution': 'Can view institution',
            'students.add_student': 'Can add student',
            'students.change_student': 'Can change student',
            'students.delete_student': 'Can delete student',
            'students.view_student': 'Can view student',
            'students.view_attendance': 'Can view attendance',
            'posts.add_post': 'Can add post',
            'posts.change_post': 'Can change post',
            'posts.delete_post': 'Can delete post',
            'posts.view_post': 'Can view post',
        },
        'Teacher': {
            'students.view_student': 'Can view student',
            'students.add_attendance': 'Can add attendance',
            'students.change_attendance': 'Can change attendance',
            'students.delete_attendance': 'Can delete attendance',
            'students.view_attendance': 'Can view attendance',
            'students.add_academicprogress': 'Can add academic progress',
            'students.change_academicprogress': 'Can change academic progress',
            'students.view_academicprogress': 'Can view academic progress',
        },
        'Guardian': {
            'students.view_student': 'Can view student',
            'students.view_academicprogress': 'Can view academic progress',
            'posts.view_post': 'Can view post',
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
                        content_type=ContentType.objects.get_for_model(User)
                    )
                    group.permissions.add(permission)
                    print(f"Permission '{permission_name}' added to group '{group_name}'.")
                except Exception as e:
                    print(f"Error creating or adding permission '{permission_name}' to group '{group_name}': {e}")
        except Exception as e:
            print(f"Error creating or getting group '{group_name}': {e}")
            
