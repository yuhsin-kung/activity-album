from datetime import date

from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Event, EventPhoto, EventDocument
from .permissions import MEMBER_GROUP


@override_settings(MEDIA_ROOT='test-media')
class EventManagementTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher',
            password='pass',
            is_staff=True,
        )
        self.student = User.objects.create_user(
            username='student',
            password='pass',
        )
        self.member_group, _ = Group.objects.get_or_create(name=MEMBER_GROUP)
        self.event = Event.objects.create(
            title='期末成果展',
            description='展示學生作品',
            date=date(2026, 6, 8),
            location='資科系館',
            created_by=self.teacher,
        )
        self.document = EventDocument.objects.create(
            event=self.event,
            title='活動企劃書',
            file=SimpleUploadedFile(
                'plan.txt',
                b'event plan',
                content_type='text/plain',
            ),
            uploaded_by=self.teacher,
        )

    def test_event_list_is_public(self):
        response = self.client.get(reverse('event-list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '期末成果展')

    def test_event_detail_is_public(self):
        response = self.client.get(reverse('event-detail', args=[self.event.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '資科系館')
        self.assertContains(response, '附件僅限系學會成員')
        self.assertNotContains(response, '活動企劃書')

    def test_signup_creates_pending_non_staff_account(self):
        response = self.client.post(reverse('member-signup'), {
            'username': 'newmember',
            'first_name': '王小明',
            'email': 'member@example.com',
            'password1': 'StrongPass12345',
            'password2': 'StrongPass12345',
        })

        user = User.objects.get(username='newmember')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.groups.filter(name=MEMBER_GROUP).exists())

    def test_pending_user_cannot_view_documents(self):
        self.client.login(username='student', password='pass')

        response = self.client.get(reverse('event-detail', args=[self.event.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '尚未完成會員審核')
        self.assertNotContains(response, '活動企劃書')

    def test_member_can_view_documents(self):
        self.student.groups.add(self.member_group)
        self.client.login(username='student', password='pass')

        response = self.client.get(reverse('event-detail', args=[self.event.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '活動企劃書')

    def test_document_download_requires_member(self):
        url = reverse('document-download', args=[self.document.pk])

        anonymous_response = self.client.get(url)
        self.assertEqual(anonymous_response.status_code, 302)
        self.assertIn('/accounts/login/', anonymous_response['Location'])

        self.client.login(username='student', password='pass')
        pending_response = self.client.get(url)
        self.assertEqual(pending_response.status_code, 403)

        self.student.groups.add(self.member_group)
        member_response = self.client.get(url)
        self.assertEqual(member_response.status_code, 200)

    def test_admin_index_redirects_to_staff_dashboard(self):
        response = self.client.get('/admin/')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/manage/')

    def test_admin_login_defaults_to_staff_dashboard(self):
        response = self.client.get('/admin/login/?next=/admin/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="/manage/"')

    def test_staff_can_approve_and_revoke_member(self):
        self.client.login(username='teacher', password='pass')

        approve_response = self.client.post(reverse('member-manage'), {
            'user_id': self.student.pk,
            'action': 'approve',
        })
        self.student.refresh_from_db()

        self.assertEqual(approve_response.status_code, 302)
        self.assertTrue(self.student.groups.filter(name=MEMBER_GROUP).exists())

        revoke_response = self.client.post(reverse('member-manage'), {
            'user_id': self.student.pk,
            'action': 'revoke',
        })
        self.student.refresh_from_db()

        self.assertEqual(revoke_response.status_code, 302)
        self.assertFalse(self.student.groups.filter(name=MEMBER_GROUP).exists())

    def test_anonymous_user_is_redirected_from_teacher_views(self):
        response = self.client.get(reverse('event-create'))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])

    def test_non_staff_user_cannot_create_event(self):
        self.client.login(username='student', password='pass')

        response = self.client.get(reverse('event-create'))

        self.assertEqual(response.status_code, 403)

    def test_staff_user_can_create_event(self):
        self.client.login(username='teacher', password='pass')

        response = self.client.post(reverse('event-create'), {
            'title': '迎新活動',
            'description': '新生交流',
            'date': '2026-09-01',
            'location': '大禮堂',
        })

        event = Event.objects.get(title='迎新活動')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(event.created_by, self.teacher)

    def test_staff_user_can_upload_photo(self):
        self.client.login(username='teacher', password='pass')
        image = SimpleUploadedFile(
            'photo.gif',
            b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;',
            content_type='image/gif',
        )

        response = self.client.post(
            reverse('photo-manage', args=[self.event.pk]),
            {'image': image, 'caption': '活動合照'},
        )

        photo = EventPhoto.objects.get(caption='活動合照')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(photo.event, self.event)
        self.assertEqual(photo.uploaded_by, self.teacher)
