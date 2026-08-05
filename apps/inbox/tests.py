from django.test import TestCase
from django.contrib.auth import get_user_model
from inbox.models import Message

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
