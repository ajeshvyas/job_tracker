import hashlib
import hmac
import base64
import time
import json
import uuid
from flask import current_app

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(raw, hashed):
    return hash_password(raw) == hashed

def base64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

def base64url_decode(data):
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)

def generate_jwt(user_id, expires_in=900):  # 15 minutes
    return _generate_token(user_id, expires_in)

def generate_refresh_token(user_id, expires_in=7 * 24 * 3600):  # 7 days
    return _generate_token(user_id, expires_in, is_refresh=True)

def _generate_token(user_id, expires_in, is_refresh=False):
    header = {"alg": "HS256", "typ": "JWT"}
    jti = str(uuid.uuid4())
    payload = {
        "user_id": user_id,
        "exp": int(time.time()) + expires_in,
        "iat": int(time.time()),
        "jti": jti,
        "type": "refresh" if is_refresh else "access"
    }

    secret = current_app.config['SECRET_KEY']
    header_b64 = base64url_encode(json.dumps(header).encode())
    payload_b64 = base64url_encode(json.dumps(payload).encode())
    signature = hmac.new(
        secret.encode(),
        f"{header_b64}.{payload_b64}".encode(),
        hashlib.sha256
    ).digest()
    signature_b64 = base64url_encode(signature)
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def verify_jwt(token):
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
        secret = current_app.config['SECRET_KEY']
        message = f"{header_b64}.{payload_b64}".encode()

        expected_sig = hmac.new(secret.encode(), message, hashlib.sha256).digest()
        expected_sig_b64 = base64url_encode(expected_sig)

        if not hmac.compare_digest(expected_sig_b64, signature_b64):
            return None

        payload_json = base64url_decode(payload_b64).decode()
        payload = json.loads(payload_json)

        if payload.get("exp") < time.time():
            return None

        return payload
    except Exception:
        return None
