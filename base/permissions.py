# permissions.py
from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_manager

class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_user

class IsAdminManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin or request.user.is_manager
