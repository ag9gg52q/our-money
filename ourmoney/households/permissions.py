from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsHouseholdMember(BasePermission):
    message = 'Nu faci parte dintr-o gospodărie.'

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.household_id is not None


class IsHouseholdAdminOrReadOnly(IsHouseholdMember):
    message = 'Doar administratorul gospodăriei poate face modificări.'

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            self.message = IsHouseholdMember.message
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_admin
