from rest_framework.permissions import BasePermission


def _is_group_member(user, group_name):
    return user.groups.filter(name=group_name).exists()


class IsAdmin(BasePermission):
    """Проверяет входит ли пользователь в группу 'admins'"""

    def has_permission(self, request, view):
        return _is_group_member(request.user, 'admins')

    def has_object_permission(self, request, view, obj):
        return _is_group_member(request.user, 'admins')


class IsUser(BasePermission):
    """Проверяет входит ли пользователь в группу 'users'"""

    def has_permission(self, request, view):
        return _is_group_member(request.user, 'users')

    def has_object_permission(self, request, view, obj):
        return _is_group_member(request.user, 'users')