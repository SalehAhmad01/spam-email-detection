from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from inbox.models import Message
from detector.models import DetectionResult

User = get_user_model()


class AnalyticsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='analyticstester', password='password123')
        self.client.login(username='analyticstester', password='password123')

        # Create sample entries
        msg1 = Message.objects.create(channel='sms', raw_text='Fraud alert BVN', sender='+2348000')
        DetectionResult.objects.create(message=msg1, label='fraud', confidence_score=0.96, language_mix='pidgin')

        msg2 = Message.objects.create(channel='email', raw_text='Legit transaction report', sender='bank@gtb.com')
        DetectionResult.objects.create(message=msg2, label='legit', confidence_score=0.99, language_mix='english')

    def test_analytics_view_authenticated(self):
        response = self.client.get(reverse('dashboard:analytics'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Threat Analytics')
        self.assertEqual(response.context['total_checked'], 2)
        self.assertEqual(response.context['fraud_count'], 1)
        self.assertEqual(response.context['legit_count'], 1)
