from pathlib import Path
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from inbox.models import Message
from detector.models import DetectionResult, FeedbackCorrection
from detector.engine import analyze_message, load_ml_model, predict_ml, FRAUD_KEYWORDS, SPAM_KEYWORDS

User = get_user_model()


class ModelCreationTests(TestCase):
    """1. Tests covering Django model creation and relationships."""

    def test_message_and_detection_result_creation(self):
        user = User.objects.create_user(username='modeluser', password='password123')
        msg = Message.objects.create(
            channel=Message.ChannelChoices.SMS,
            raw_text="ALERT: Abnormal login attempt detected on your mobile banking app.",
            sender="+234803990011",
            submitted_by=user
        )
        self.assertEqual(Message.objects.count(), 1)
        self.assertIn("SMS", str(msg))

        result = DetectionResult.objects.create(
            message=msg,
            label=DetectionResult.LabelChoices.FRAUD,
            confidence_score=0.97,
            flagged_keywords=['unusual login', 'security alert'],
            language_mix='english',
            model_version='v1.0-test'
        )
        self.assertEqual(DetectionResult.objects.count(), 1)
        self.assertEqual(result.message, msg)
        self.assertIn("Fraud", str(result))

        correction = FeedbackCorrection.objects.create(
            detection_result=result,
            corrected_label=DetectionResult.LabelChoices.LEGIT,
            corrected_by=user,
            note="Verified internal security notice."
        )
        self.assertEqual(FeedbackCorrection.objects.count(), 1)
        self.assertEqual(correction.detection_result, result)
        self.assertEqual(correction.corrected_by, user)


class DetectionEngineRuleTests(TestCase):
    """2. Tests covering detection engine's rule-based flags on known scam-pattern examples."""

    def test_bvn_phishing_scam(self):
        text = "URGENT: Your BVN has been flagged for non-compliance. Re-validate immediately at http://cbn-audit-portal.ng"
        res = analyze_message(text)
        self.assertEqual(res['label'], 'fraud')
        self.assertIn('bvn', res['flagged_keywords'])
        self.assertGreaterEqual(res['confidence_score'], 0.85)

    def test_nin_deactivation_scam(self):
        text = "Your NIN registration is incomplete and will be deactivated in 24 hours. Send your NIN immediately."
        res = analyze_message(text)
        self.assertEqual(res['label'], 'fraud')
        self.assertTrue(any(kw in res['flagged_keywords'] for kw in ['nin', 'deactivated']))

    def test_atm_pin_otp_scam(self):
        text = "This is your bank calling. Send your card number, PIN and OTP to reactivate your blocked ATM card."
        res = analyze_message(text)
        self.assertEqual(res['label'], 'fraud')
        self.assertTrue(set(['pin', 'otp', 'atm card']).intersection(res['flagged_keywords']))

    def test_lottery_promo_spam(self):
        text = "CONGRATULATIONS! You won N500,000 from MTN Promo! Call 08023456789 to claim your cash reward now."
        res = analyze_message(text)
        self.assertEqual(res['label'], 'spam')
        self.assertTrue(any(kw in res['flagged_keywords'] for kw in ['won', 'promo', 'claim', 'cash reward']))

    def test_cheap_collateral_loan_spam(self):
        text = "Cheap loan available! No collateral, no stress. Get 200k in 1 hour."
        res = analyze_message(text)
        self.assertEqual(res['label'], 'spam')
        self.assertTrue(any(kw in res['flagged_keywords'] for kw in ['cheap loan', 'no collateral', '200k']))

    def test_legitimate_bank_alert(self):
        text = "Your GTBank account was credited with NGN 45,000.00 on 03-AUG-2026. Available balance is NGN 132,450.00."
        res = analyze_message(text)
        self.assertEqual(res['label'], 'legit')
        self.assertEqual(len(res['flagged_keywords']), 0)
        self.assertEqual(res['confidence_score'], 0.95)

    def test_pidgin_language_detection(self):
        text = "Abeg dey wait for me o, wetin dey happen for house baba sharp sharp wahala dem oya"
        res = analyze_message(text)
        self.assertEqual(res['language_mix'], 'pidgin')

    def test_mixed_language_detection(self):
        text = "Hey bro, I dey reach your side by 4pm for the meeting"
        res = analyze_message(text)
        self.assertEqual(res['language_mix'], 'mixed')

    def test_empty_message_handling(self):
        res = analyze_message("")
        self.assertEqual(res['label'], 'legit')
        self.assertEqual(res['confidence_score'], 1.0)


class MLPipelineExecutionTests(TestCase):
    """3. Tests covering ML pipeline loading and predicting without crashing."""

    def test_load_ml_model_missing_file_fallback(self):
        model = load_ml_model()
        self.assertTrue(model is None or hasattr(model, 'predict'))

    def test_predict_ml_without_crashing(self):
        res = predict_ml("Sample text message input for ML test")
        self.assertIsInstance(res, dict)
        self.assertIn('label', res)
        self.assertIn('confidence', res)
        self.assertIn('source', res)

    def test_predict_ml_with_mock_pipeline(self):
        class DummyMLPipeline:
            def predict(self, texts):
                return ['fraud']

            def predict_proba(self, texts):
                return [[0.05, 0.05, 0.90]]

        import detector.engine
        original_cache = detector.engine._ML_MODEL_CACHE
        detector.engine._ML_MODEL_CACHE = DummyMLPipeline()

        try:
            res = predict_ml("Test scam text")
            self.assertEqual(res['label'], 'fraud')
            self.assertAlmostEqual(res['confidence'], 0.90)
            self.assertEqual(res['source'], 'ml_pipeline')
        finally:
            detector.engine._ML_MODEL_CACHE = original_cache


class ViewAccessControlTests(TestCase):
    """4. Tests covering view access control (login_required redirects for unauthenticated users)."""

    def setUp(self):
        self.client = Client()

    def test_dashboard_home_redirects_unauthenticated(self):
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_dashboard_analytics_redirects_unauthenticated(self):
        response = self.client.get(reverse('dashboard:analytics'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_inbox_submit_redirects_unauthenticated(self):
        response = self.client.get(reverse('inbox:submit'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_inbox_history_redirects_unauthenticated(self):
        response = self.client.get(reverse('inbox:history'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_inbox_list_redirects_unauthenticated(self):
        response = self.client.get(reverse('inbox:list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_authenticated_access_allowed(self):
        user = User.objects.create_user(username='autheduser', password='password123')
        self.client.login(username='autheduser', password='password123')

        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('inbox:submit'))
        self.assertEqual(response.status_code, 200)
