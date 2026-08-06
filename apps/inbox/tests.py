from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from inbox.models import Message
from detector.models import DetectionResult
from detector.engine import analyze_message

User = get_user_model()


class MessageModelTest(TestCase):
    def test_create_message(self):
        user = User.objects.create_user(username='testuser', password='password123')
        msg = Message.objects.create(
            channel=Message.ChannelChoices.SMS,
            raw_text="Urgent BVN update required.",
            sender="+2348000000000",
            submitted_by=user
        )
        self.assertEqual(Message.objects.count(), 1)
        self.assertIn("BVN update", str(msg))


class DetectorEngineTest(TestCase):
    def test_engine_fraud_detection(self):
        analysis = analyze_message("Urgent: Your BVN has been flagged for non-compliance. Click http://cbn-audit.ng")
        self.assertEqual(analysis['label'], 'fraud')
        self.assertIn('bvn', analysis['flagged_keywords'])
        self.assertGreaterEqual(analysis['confidence_score'], 0.85)

    def test_engine_pidgin_detection(self):
        analysis = analyze_message("Abeg dey wait for me o, wetin dey happen for house baba")
        self.assertEqual(analysis['language_mix'], 'pidgin')


class InboxViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='password123')
        self.client.login(username='tester', password='password123')

    def test_submit_message_redirects_to_result(self):
        response = self.client.post(reverse('inbox:submit'), {
            'submit_single': '1',
            'channel': 'sms',
            'sender': '+2348030000000',
            'raw_text': 'Your BVN registration is incomplete. Reply immediately to prevent account freeze.'
        })
        self.assertEqual(response.status_code, 302)
        result = DetectionResult.objects.first()
        self.assertIsNotNone(result)
        self.assertEqual(result.label, 'fraud')
        self.assertIn(reverse('inbox:result', kwargs={'pk': result.pk}), response.url)

    def test_result_detail_view(self):
        msg = Message.objects.create(channel='sms', raw_text='Test scam promo', sender='+234800000')
        result = DetectionResult.objects.create(
            message=msg,
            label='spam',
            confidence_score=0.88,
            flagged_keywords=['promo'],
            language_mix='english'
        )
        response = self.client.get(reverse('inbox:result', kwargs={'pk': result.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SPAM')
        self.assertContains(response, '88%')
