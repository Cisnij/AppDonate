from rest_framework.permissions import BasePermission
from relationship.selectors import is_blocked

class IsNotBlocked(BasePermission):
    message = "Bạn không có quyền truy cập trang này" #false thì tự raise message này

    def has_object_permission(self, request, view, obj):
        return not is_blocked(page_id=obj, user_id=request.user.id)# false là có block còn true là không