from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

MEMBER_GROUP = '系學會會員'


def can_view_documents(user):
    """老師或會員群組成員可以查看附件。"""
    if not user.is_authenticated:
        return False
    return user.is_staff or user.groups.filter(name=MEMBER_GROUP).exists()


class TeacherRequiredMixin(LoginRequiredMixin):
    """只允許 staff（老師）操作。"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_staff:
            raise PermissionDenied('此功能限老師使用')
        return super().dispatch(request, *args, **kwargs)


class MemberRequiredMixin(LoginRequiredMixin):
    """只允許老師或會員群組成員存取。"""

    login_url = 'member-login'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not can_view_documents(request.user):
            raise PermissionDenied('此功能限系學會成員使用')
        return super().dispatch(request, *args, **kwargs)
