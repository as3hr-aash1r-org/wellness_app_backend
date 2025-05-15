from firebase_admin import auth
from firebase_admin._auth_utils import InvalidIdTokenError


def verify_firebase_token(id_token: str):
    try:
        decoded = auth.verify_id_token(id_token)
        return decoded
    except InvalidIdTokenError:
        return None
