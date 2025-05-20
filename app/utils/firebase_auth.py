# import firebase_admin
# from firebase_admin import auth, credentials

# # Only once during startup
# cred = credentials.Certificate("/home/aashir/Documents/wellness_service_account_key.json")
# firebase_admin.initialize_app(cred)

# def verify_firebase_token(id_token: str):
#     try:
#         decoded_token = auth.verify_id_token(id_token)
#         return decoded_token
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="Invalid Firebase token")
