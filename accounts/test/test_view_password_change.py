from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User


class LoginRequiredPasswordChangeTests(TestCase):
    def test_redirection(self):
        url = reverse('password_change')
        login_url = reverse('login')

        response = self.client.get(url)
        self.assertRedirects(response, f'{login_url}?next={url}')


class PasswordChangeTestCase(TestCase):
    def setUp(self, data=None):
        if data is None:
            data = {}
        self.user = User.objects.create_user(username='john', email='john@doe.com', password='old_password')
        self.url = reverse('password_change')
        self.client.login(username='john', password='old_password')
        self.response = self.client.post(self.url, data)
