from firebase_admin import auth
from fastapi import Depends, Header, HTTPException, APIRouter

router = APIRouter(prefix="/test")


def generate_test_token(uid: str, phone_number: str):
    try:
        user = auth.get_user(uid)
    except:
        user = auth.create_user(uid=uid, phone_number=phone_number)
    custom_token = auth.create_custom_token(uid)
    print("Custom token (JWT, dev only):", custom_token.decode())


generate_test_token("dev_user_123", "+923311234567")


def get_current_user_dev(authorization: str = Header(...)):
    return {
        "uid": "dev_user_123",
        "phone": "+923311234567"
    }


@router.get("/me")
def get_user(user_info=Depends(get_current_user_dev)):
    return user_info
