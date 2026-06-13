from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.contrib.auth.views import LoginView
from django.http import FileResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView
from django.shortcuts import get_object_or_404

from .forms import EventForm, PhotoUploadForm, DocumentUploadForm, MemberSignUpForm
from .models import Event, EventPhoto, EventDocument
from .permissions import TeacherRequiredMixin, MemberRequiredMixin, can_view_documents, MEMBER_GROUP


# ── 公開頁面 ──────────────────────────────────────────────

class EventListView(ListView):
    model = Event
    template_name = 'albums/event_list.html'
    context_object_name = 'past_events'

    def get_queryset(self):
        today = timezone.now().date()
        return Event.objects.filter(start_date__lte=today).order_by('-start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated and (
            user.is_staff or user.groups.filter(name=MEMBER_GROUP).exists()
        ):
            today = timezone.now().date()
            context['future_events'] = Event.objects.filter(
                start_date__gt=today
            ).order_by('start_date')
        return context


class MemberLoginView(LoginView):
    template_name = 'albums/member_login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        # 有指定 next 就用 next，否則老師去後台、一般會員回首頁
        redirect_url = self.get_redirect_url()
        if redirect_url:
            return redirect_url
        if self.request.user.is_staff:
            return reverse('staff-dashboard')
        return reverse('event-list')


class MemberSignUpView(CreateView):
    form_class = MemberSignUpForm
    template_name = 'albums/member_signup.html'
    success_url = reverse_lazy('member-login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            '帳號已建立，請等待老師審核並加入系學會成員後，即可查看附件。',
        )
        return response


class EventDetailView(DetailView):
    model = Event
    template_name = 'albums/event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = self.object.photos.all()
        context['can_view_docs'] = can_view_documents(self.request.user)
        context['has_documents'] = self.object.documents.exists()
        if context['can_view_docs']:
            context['documents'] = self.object.documents.all()
        return context


class DocumentDownloadView(MemberRequiredMixin, DetailView):
    model = EventDocument
    pk_url_kwarg = 'doc_pk'

    def get(self, request, *args, **kwargs):
        document = self.get_object()
        return FileResponse(
            document.file.open('rb'),
            as_attachment=False,
            filename=document.filename(),
        )


# ── 老師後台 ──────────────────────────────────────────────

class StaffDashboardView(TeacherRequiredMixin, ListView):
    model = Event
    template_name = 'albums/manage/dashboard.html'
    context_object_name = 'events'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_photos'] = EventPhoto.objects.count()
        context['total_docs'] = EventDocument.objects.count()
        return context


class MemberManagementView(TeacherRequiredMixin, ListView):
    model = User
    template_name = 'albums/manage/member_manage.html'
    context_object_name = 'users'

    def get_member_group(self):
        group, _ = Group.objects.get_or_create(name=MEMBER_GROUP)
        return group

    def get_queryset(self):
        return (
            User.objects
            .filter(is_staff=False, is_superuser=False)
            .prefetch_related('groups')
            .order_by('date_joined', 'username')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.get_member_group()
        users = list(context['users'])
        context['member_group'] = group
        context['pending_users'] = [user for user in users if group not in user.groups.all()]
        context['approved_users'] = [user for user in users if group in user.groups.all()]
        return context

    def post(self, request, *args, **kwargs):
        group = self.get_member_group()
        user = get_object_or_404(
            User,
            pk=request.POST.get('user_id'),
            is_staff=False,
            is_superuser=False,
        )
        action = request.POST.get('action')

        if action == 'approve':
            user.groups.add(group)
            messages.success(request, f'已核准 {user.username} 為系學會成員。')
        elif action == 'revoke':
            user.groups.remove(group)
            messages.success(request, f'已移除 {user.username} 的系學會成員資格。')

        return redirect('member-manage')


class EventCreateView(TeacherRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'albums/manage/event_form.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, '活動已建立！現在可以在下方新增照片和附件。')
        return response

    def get_success_url(self):
        return reverse('event-media', kwargs={'pk': self.object.pk})


class EventUpdateView(TeacherRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'albums/manage/event_form.html'
    success_url = reverse_lazy('staff-dashboard')


class EventMediaView(TeacherRequiredMixin, DetailView):
    model = Event
    template_name = 'albums/manage/event_media.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = self.object.photos.all()
        context['documents'] = self.object.documents.all()
        return context


class EventDeleteView(TeacherRequiredMixin, DeleteView):
    model = Event
    template_name = 'albums/manage/event_confirm_delete.html'
    success_url = reverse_lazy('staff-dashboard')


class PhotoManageView(TeacherRequiredMixin, CreateView):
    model = EventPhoto
    form_class = PhotoUploadForm

    def get_event(self):
        return get_object_or_404(Event, pk=self.kwargs['event_pk'])

    def get(self, request, *args, **kwargs):
        return redirect(reverse('event-media', kwargs={'pk': self.kwargs['event_pk']}) + '#photos')

    def post(self, request, *args, **kwargs):
        event = self.get_event()
        files = request.FILES.getlist('image')
        for f in files:
            EventPhoto.objects.create(
                event=event,
                image=f,
                uploaded_by=request.user,
            )
        return redirect(reverse('event-media', kwargs={'pk': event.pk}) + '#photos')


class PhotoDeleteView(TeacherRequiredMixin, DeleteView):
    model = EventPhoto
    template_name = 'albums/manage/photo_confirm_delete.html'

    def get_success_url(self):
        return reverse('event-media', kwargs={'pk': self.object.event.pk}) + '#photos'


class DocumentManageView(TeacherRequiredMixin, CreateView):
    model = EventDocument
    form_class = DocumentUploadForm

    def get_event(self):
        return get_object_or_404(Event, pk=self.kwargs['event_pk'])

    def get(self, request, *args, **kwargs):
        return redirect(reverse('event-media', kwargs={'pk': self.kwargs['event_pk']}) + '#documents')

    def form_valid(self, form):
        form.instance.event = self.get_event()
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('event-media', kwargs={'pk': self.kwargs['event_pk']}) + '#documents'


class DocumentDeleteView(TeacherRequiredMixin, DeleteView):
    model = EventDocument
    template_name = 'albums/manage/document_confirm_delete.html'

    def get_success_url(self):
        return reverse('event-media', kwargs={'pk': self.object.event.pk}) + '#documents'


class TeacherManagementView(TeacherRequiredMixin, ListView):
    model = User
    template_name = 'albums/manage/teacher_manage.html'
    context_object_name = 'users'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return (
            User.objects
            .filter(is_superuser=False)
            .order_by('date_joined', 'username')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = list(context['users'])
        member_group_name = MEMBER_GROUP
        context['teacher_users'] = [u for u in users if u.is_staff]
        context['non_teacher_users'] = [
            u for u in users
            if not u.is_staff and not u.groups.filter(name=member_group_name).exists()
        ]
        return context

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=request.POST.get('user_id'), is_superuser=False)
        action = request.POST.get('action')
        if action == 'grant':
            user.is_staff = True
            user.save()
            messages.success(request, f'已將 {user.username} 設為管理員。')
        elif action == 'revoke':
            user.is_staff = False
            user.save()
            messages.success(request, f'已移除 {user.username} 的管理員身分。')
        return redirect('teacher-manage')
