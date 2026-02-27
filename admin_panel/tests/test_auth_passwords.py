from django.test import SimpleTestCase

from admin_panel.models import SupportClient, User
from core.hashers import WerkzeugPBKDF2SHA256PasswordHasher


class AuthPasswordCompatibilityTests(SimpleTestCase):
    def _legacy_hash(self):
        return WerkzeugPBKDF2SHA256PasswordHasher().encode(
            password='pass1234',
            salt='testsalt123',
            iterations=260000,
        )

    def test_user_check_password_supports_legacy_werkzeug_hash(self):
        user = User()
        user.password = self._legacy_hash()
        self.assertTrue(user.check_password('pass1234'))
        self.assertFalse(user.check_password('wrongpass'))

    def test_support_client_check_password_supports_legacy_werkzeug_hash(self):
        client = SupportClient()
        client.password_hash = self._legacy_hash()
        self.assertTrue(client.check_password('pass1234'))
        self.assertFalse(client.check_password('wrongpass'))
