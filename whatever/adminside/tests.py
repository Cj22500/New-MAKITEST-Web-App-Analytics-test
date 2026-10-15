from django.test import TestCase
from django.urls import reverse

from homepage.models import CustomUser


class TeacherAuthorizationTests(TestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_user(
            'site-admin', role='admin', password='test-password'
        )
        self.teacher = CustomUser.objects.create_user(
            'teacher', role='teacher', password='test-password'
        )

    def test_admin_can_authorize_and_unauthorize_teacher(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('admin_home'))
        self.assertContains(response, 'Teacher Authorization')
        self.assertContains(response, 'Not authorized')

        response = self.client.post(
            reverse('set_teacher_authorization', args=[self.teacher.pk]),
            {'authorized': 'true'},
        )
        self.assertRedirects(response, reverse('admin_home'))
        self.teacher.refresh_from_db()
        self.assertTrue(self.teacher.authorized)

        response = self.client.post(
            reverse('set_teacher_authorization', args=[self.teacher.pk]),
            {'authorized': 'false'},
        )
        self.assertRedirects(response, reverse('admin_home'))
        self.teacher.refresh_from_db()
        self.assertFalse(self.teacher.authorized)

    def test_only_admin_can_manage_authorization(self):
        student = CustomUser.objects.create_user('student', role='student')
        self.client.force_login(student)
        self.assertEqual(self.client.get(reverse('admin_home')).status_code, 403)
        self.assertEqual(
            self.client.post(
                reverse('set_teacher_authorization', args=[self.teacher.pk]),
                {'authorized': 'true'},
            ).status_code,
            403,
        )

    def test_unauthorized_teacher_is_blocked_from_teacher_pages(self):
        self.client.force_login(self.teacher)
        self.assertEqual(self.client.get(reverse('teacher_home')).status_code, 403)