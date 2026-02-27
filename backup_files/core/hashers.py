import hashlib

from django.contrib.auth.hashers import BasePasswordHasher
from django.utils.crypto import constant_time_compare, pbkdf2
from django.utils.translation import gettext_noop as _


class WerkzeugPBKDF2SHA256PasswordHasher(BasePasswordHasher):
    algorithm = 'werkzeug_pbkdf2_sha256'

    def salt(self):
        return super().salt()

    def encode(self, password, salt, iterations=260000):
        assert password is not None
        assert salt and '$' not in salt
        digest = pbkdf2(password, salt, iterations, digest=hashlib.sha256).hex()
        return f'pbkdf2:sha256:{int(iterations)}${salt}${digest}'

    def decode(self, encoded):
        algorithm, salt, hash_value = encoded.split('$', 2)
        _, _, iter_str = algorithm.split(':', 2)
        return {
            'algorithm': self.algorithm,
            'iterations': int(iter_str),
            'salt': salt,
            'hash': hash_value,
        }

    def verify(self, password, encoded):
        if not self.identify(encoded):
            return False
        decoded = self.decode(encoded)
        encoded_2 = self.encode(password, decoded['salt'], decoded['iterations'])
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        decoded = self.decode(encoded)
        return {
            _('algorithm'): self.algorithm,
            _('iterations'): decoded['iterations'],
            _('salt'): decoded['salt'][:4] + '...',
            _('hash'): decoded['hash'][:8] + '...',
        }

    def must_update(self, encoded):
        return False

    def harden_runtime(self, password, encoded):
        return

    def identify(self, encoded):
        return str(encoded).startswith('pbkdf2:sha256:') and '$' in str(encoded)
