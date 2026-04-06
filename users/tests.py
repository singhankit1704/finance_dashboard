# users/tests.py
from django.test import TestCase
from django.urls import reverse
from .models import User


class AuthTests(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username='testadmin',
            password='Admin@123',
            role='admin'
        )
        self.viewer = User.objects.create_user(
            username='testviewer',
            password='Viewer@123',
            role='viewer'
        )

    def _get_token(self, username, password):
        response = self.client.post(reverse('login'), {
            'username': username,
            'password': password
        }, content_type='application/json')
        return response.json()['data']['access']

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'testadmin',
            'password': 'Admin@123'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.json()['data'])

    def test_login_wrong_password(self):
        response = self.client.post(reverse('login'), {
            'username': 'testadmin',
            'password': 'wrongpass'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_viewer_cannot_create_user(self):
        token = self._get_token('testviewer', 'Viewer@123')
        response = self.client.post(
            reverse('user-list-create'),
            {'username': 'newuser', 'password': 'Test@1234', 'role': 'viewer'},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_can_list_users(self):
        token = self._get_token('testadmin', 'Admin@123')
        response = self.client.get(
            reverse('user-list-create'),
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEqual(response.status_code, 200)