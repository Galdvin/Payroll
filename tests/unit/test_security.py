from datetime import timedelta
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)


def test_password_hashing():
    password = "SecurePassword123!"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_access_token_creation_and_decoding():
    user_id = 42
    token = create_access_token(subject=user_id, extra_claims={"role": "admin"})
    payload = decode_token(token)

    assert payload is not None
    assert payload.get("sub") == str(user_id)
    assert payload.get("type") == "access"
    assert payload.get("role") == "admin"


def test_jwt_refresh_token_creation():
    user_id = 99
    token = create_refresh_token(subject=user_id)
    payload = decode_token(token)

    assert payload is not None
    assert payload.get("sub") == str(user_id)
    assert payload.get("type") == "refresh"


def test_invalid_jwt_token_decoding():
    invalid_token = "invalid.jwt.token.string"
    payload = decode_token(invalid_token)
    assert payload is None
