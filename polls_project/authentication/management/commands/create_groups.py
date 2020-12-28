from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model

User = get_user_model()

GROUPS = {
    'admins': [
        'Can add Token', 'Can delete Token', 'Can view Token',
        'Can add choice', 'Can change choice', 'Can delete choice',
        'Can view choice', 'Can add poll', 'Can change poll',
        'Can delete poll', 'Can view poll', 'Can add question',
        'Can change question', 'Can delete question', 'Can view question'
    ],
    'users': [
        'Can add Token', 'Can delete Token', 'Can view Token',
        'Can add answer', 'Can view answer', 'Can add passed poll',
        'Can view passed poll', 'Can view poll'
    ]
}


class Command(BaseCommand):
    help = 'Создает группы'

    def handle(self, *args, **options):
        for group_name in GROUPS:
            group, _ = Group.objects.get_or_create(name=group_name)

            for perm_name in GROUPS[group_name]:
                try:
                    permission = Permission.objects.get(name=perm_name)
                except Permission.DoesNotExist:
                    continue
                group.permissions.add(permission)

            if group_name == 'admins':
                admin = User(username='admin')
                admin.set_password('adminadmin')
                admin.save()
                admin.groups.add(group)

            if group_name == 'users':
                user = User(username='user')
                user.set_password('useruser')
                user.save()
                user.groups.add(group)
