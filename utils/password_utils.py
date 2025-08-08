import base64
import json

from extensions.init_bcrypt import bcrypt


def get_hashed_password(password: str) -> str:
    return bcrypt.hash(password) if password else None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.verify(plain_password, hashed_password)

def decode_jwt_part(part):
    # Pad the Base64 string if needed
    padded = part + '=' * (-len(part) % 4)
    decoded_bytes = base64.urlsafe_b64decode(padded)
    return json.loads(decoded_bytes)