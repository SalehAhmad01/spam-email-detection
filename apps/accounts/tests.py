from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthViewsTest(TestCase):
    def test_login_redirect(self):
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('accounts:login'), response.url)

    def test_register_and_login(self):
        register_url = reverse('accounts:register')
        response = self.client.post(register_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
