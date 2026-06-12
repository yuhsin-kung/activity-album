from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # 會員帳號
    path('accounts/login/', views.MemberLoginView.as_view(), name='member-login'),
    path('accounts/signup/', views.MemberSignUpView.as_view(), name='member-signup'),
    path('accounts/logout/', LogoutView.as_view(), name='member-logout'),

    # 公開頁面
    path('', views.EventListView.as_view(), name='event-list'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('documents/<int:doc_pk>/download/', views.DocumentDownloadView.as_view(), name='document-download'),

    # 老師後台
    path('manage/', views.StaffDashboardView.as_view(), name='staff-dashboard'),
    path('manage/members/', views.MemberManagementView.as_view(), name='member-manage'),
    path('manage/teachers/', views.TeacherManagementView.as_view(), name='teacher-manage'),
    path('manage/create/', views.EventCreateView.as_view(), name='event-create'),
    path('manage/<int:pk>/edit/', views.EventUpdateView.as_view(), name='event-update'),
    path('manage/<int:pk>/media/', views.EventMediaView.as_view(), name='event-media'),
    path('manage/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event-delete'),

    # 照片管理
    path('manage/<int:event_pk>/photos/', views.PhotoManageView.as_view(), name='photo-manage'),
    path('manage/<int:event_pk>/photos/<int:pk>/delete/', views.PhotoDeleteView.as_view(), name='photo-delete'),

    # 附件管理
    path('manage/<int:event_pk>/documents/', views.DocumentManageView.as_view(), name='document-manage'),
    path('manage/<int:event_pk>/documents/<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='document-delete'),
]
