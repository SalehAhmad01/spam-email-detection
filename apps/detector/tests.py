from django.test import TestCase
from inbox.models import Message
from detector.models import DetectionResult, FeedbackCorrection


class DetectionModelTest(TestCase):
    def test_create_detection_result(self):
        msg = Message.objects.create(
            channel=Message.ChannelChoices.EMAIL,
            raw_text="Phishing email test",
            sender="scam@phish.ng"
        )
        result = DetectionResult.objects.create(
            message=msg,
            label=DetectionResult.LabelChoices.FRAUD,
            confidence_score=0.98,
            flagged_keywords=["phishing", "cbn"]
        )
        self.assertEqual(DetectionResult.objects.count(), 1)
        self.assertEqual(result.label, 'fraud')

        correction = FeedbackCorrection.objects.create(
            detection_result=result,
            corrected_label=DetectionResult.LabelChoices.LEGIT,
            note="False positive test"
        )
        self.assertEqual(FeedbackCorrection.objects.count(), 1)
