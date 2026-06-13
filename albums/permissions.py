from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


def can_view_documents(user):
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    from .models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile.is_member


class TeacherRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_staff:
            raise PermissionDenied('此功能限老師使用')
        return super().dispatch(request, *args, **kwargs)


class MemberRequiredMixin(LoginRequiredMixin):
    login_url = 'member-login'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not can_view_documents(request.user):
            raise PermissionDenied('此功能限系學會成員使用')
        return super().dispatch(request, *args, **kwargs)
