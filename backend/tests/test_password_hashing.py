"""
Password Hashing Tests

verify_password must fail closed: only bcrypt hashes ever verify, never
plaintext or other digest formats stored in the password_hash column.
"""

from app.core.security import get_password_hash, verify_password


class TestVerifyPassword:
    def test_accepts_matching_bcrypt_hash(self):
        hashed = get_password_hash("Correct-horse-1!")

        assert verify_password("Correct-horse-1!", hashed) is True

    def test_rejects_wrong_password(self):
        hashed = get_password_hash("Correct-horse-1!")

        assert verify_password("wrong-password", hashed) is False

    def test_rejects_plaintext_stored_value(self):
        assert verify_password("secret", "secret") is False

    def test_rejects_sha256_stored_value(self):
        import hashlib

        sha256_hash = hashlib.sha256(b"secret").hexdigest()

        assert verify_password("secret", sha256_hash) is False

    def test_rejects_empty_stored_hash(self):
        assert verify_password("secret", "") is False

    def test_bcrypt_hash_output_is_bcrypt_formatted(self):
        assert get_password_hash("secret").startswith("$2")
