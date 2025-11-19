"""
OAuth Token Encryption Utilities
=================================
Provides encryption/decryption for OAuth tokens at rest using Fernet (AES-128-CBC).

SECURITY REQUIREMENTS:
- All OAuth access tokens and refresh tokens MUST be encrypted before database storage
- Encryption key MUST be stored in environment variable CALENDAR_ENCRYPTION_KEY
- Key rotation supported via CALENDAR_ENCRYPTION_KEY_OLD for zero-downtime rotation

Usage:
    from utils.token_encryption import encrypt_token, decrypt_token

    # Encrypt before storage
    encrypted = encrypt_token(access_token)
    db.insert("calendar_connections", {"access_token": encrypted})

    # Decrypt after retrieval
    connection = db.select("calendar_connections", ...)
    access_token = decrypt_token(connection["access_token"])
"""

import os
import base64
import logging
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)


class TokenEncryptionError(Exception):
    """Raised when token encryption/decryption fails"""
    pass


def _get_cipher():
    """
    Get Fernet cipher instance from environment variable.

    Returns:
        Fernet: Encryption cipher

    Raises:
        TokenEncryptionError: If CALENDAR_ENCRYPTION_KEY not set or invalid
    """
    key = os.getenv("CALENDAR_ENCRYPTION_KEY")

    if not key:
        error_msg = (
            "CALENDAR_ENCRYPTION_KEY environment variable is required for OAuth token encryption. "
            "Generate with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
        )
        logger.error(error_msg)
        raise TokenEncryptionError(error_msg)

    try:
        return Fernet(key.encode() if isinstance(key, str) else key)
    except Exception as e:
        raise TokenEncryptionError(f"Invalid CALENDAR_ENCRYPTION_KEY format: {e}")


def _get_old_cipher() -> Optional[Fernet]:
    """
    Get old cipher for key rotation support.

    Returns:
        Optional[Fernet]: Old cipher if CALENDAR_ENCRYPTION_KEY_OLD is set, else None
    """
    old_key = os.getenv("CALENDAR_ENCRYPTION_KEY_OLD")
    if not old_key:
        return None

    try:
        return Fernet(old_key.encode() if isinstance(old_key, str) else old_key)
    except Exception as e:
        logger.warning(f"Invalid CALENDAR_ENCRYPTION_KEY_OLD format: {e}")
        return None


def encrypt_token(token: str) -> str:
    """
    Encrypt an OAuth token for secure storage.

    Args:
        token: Plain text OAuth token (access_token or refresh_token)

    Returns:
        str: Base64-encoded encrypted token

    Raises:
        TokenEncryptionError: If encryption fails

    Example:
        >>> encrypted = encrypt_token("ya29.a0AfH6SMB...")
        >>> encrypted
        'gAAAAABh8...'  # Base64-encoded ciphertext
    """
    if not token:
        raise TokenEncryptionError("Token cannot be empty")

    try:
        cipher = _get_cipher()
        encrypted_bytes = cipher.encrypt(token.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')
    except Exception as e:
        logger.error(f"Token encryption failed: {e}")
        raise TokenEncryptionError(f"Encryption failed: {e}")


def decrypt_token(encrypted_token: str) -> str:
    """
    Decrypt an OAuth token from storage.

    Supports key rotation: tries current key first, falls back to old key if set.

    Args:
        encrypted_token: Base64-encoded encrypted token from database

    Returns:
        str: Plain text OAuth token

    Raises:
        TokenEncryptionError: If decryption fails with both current and old keys

    Example:
        >>> decrypted = decrypt_token('gAAAAABh8...')
        >>> decrypted
        'ya29.a0AfH6SMB...'
    """
    if not encrypted_token:
        raise TokenEncryptionError("Encrypted token cannot be empty")

    # Try current key first
    try:
        cipher = _get_cipher()
        decrypted_bytes = cipher.decrypt(encrypted_token.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')
    except InvalidToken:
        # Try old key for rotation support
        old_cipher = _get_old_cipher()
        if old_cipher:
            try:
                decrypted_bytes = old_cipher.decrypt(encrypted_token.encode('utf-8'))
                logger.info("Token decrypted with old key - consider re-encrypting with new key")
                return decrypted_bytes.decode('utf-8')
            except InvalidToken:
                pass

        # Both keys failed
        error_msg = "Token decryption failed - token may be corrupted or keys rotated"
        logger.error(error_msg)
        raise TokenEncryptionError(error_msg)
    except Exception as e:
        logger.error(f"Token decryption failed: {e}")
        raise TokenEncryptionError(f"Decryption failed: {e}")


def rotate_token_encryption(encrypted_token: str) -> str:
    """
    Re-encrypt a token with the current key (for key rotation).

    Usage during key rotation:
    1. Set CALENDAR_ENCRYPTION_KEY_OLD to old key
    2. Set CALENDAR_ENCRYPTION_KEY to new key
    3. Run migration to re-encrypt all tokens
    4. Remove CALENDAR_ENCRYPTION_KEY_OLD

    Args:
        encrypted_token: Token encrypted with old key

    Returns:
        str: Token re-encrypted with new key

    Example:
        >>> # After rotating keys
        >>> tokens = db.select("calendar_connections", ["access_token"])
        >>> for token in tokens:
        >>>     new_encrypted = rotate_token_encryption(token["access_token"])
        >>>     db.update("calendar_connections", id, {"access_token": new_encrypted})
    """
    try:
        # Decrypt with old key, encrypt with new key
        plain_token = decrypt_token(encrypted_token)
        return encrypt_token(plain_token)
    except Exception as e:
        logger.error(f"Token rotation failed: {e}")
        raise TokenEncryptionError(f"Rotation failed: {e}")


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key.

    Returns:
        str: Base64-encoded 32-byte key suitable for CALENDAR_ENCRYPTION_KEY

    Example:
        >>> key = generate_encryption_key()
        >>> print(f"Add to .env: CALENDAR_ENCRYPTION_KEY={key}")
    """
    key = Fernet.generate_key()
    return key.decode('utf-8')


# Validation helper
def validate_encryption_setup() -> bool:
    """
    Validate that encryption is properly configured.

    Returns:
        bool: True if encryption is configured correctly

    Raises:
        TokenEncryptionError: If configuration is invalid
    """
    try:
        # Try to get cipher (will raise if key is missing/invalid)
        cipher = _get_cipher()

        # Test encryption/decryption roundtrip
        test_token = "test_token_12345"
        encrypted = encrypt_token(test_token)
        decrypted = decrypt_token(encrypted)

        if decrypted != test_token:
            raise TokenEncryptionError("Encryption roundtrip test failed")

        logger.info("OAuth token encryption is properly configured")
        return True

    except Exception as e:
        logger.error(f"Encryption validation failed: {e}")
        raise


if __name__ == "__main__":
    # CLI utility for key generation
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "generate-key":
        key = generate_encryption_key()
        print(f"\nGenerated encryption key:\n{key}\n")
        print("Add to your .env file:")
        print(f"CALENDAR_ENCRYPTION_KEY={key}\n")
    else:
        print("Usage: python token_encryption.py generate-key")
