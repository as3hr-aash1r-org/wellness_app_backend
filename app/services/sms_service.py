import requests
from typing import Dict, Any
from app.core.settings import settings


class SMSService:
    """Service for sending SMS via SMS.to API"""
    
    BASE_URL = "https://api.sms.to/sms/send"
    
    @staticmethod
    def send_otp(phone_number: str, otp_code: str) -> Dict[str, Any]:
        """
        Send OTP via SMS.to
        
        Args:
            phone_number: Recipient phone number (with country code)
            otp_code: The OTP code to send
            
        Returns:
            Dict with success status and message
        """
        try:
            message = f"Your verification code is: {otp_code}. Valid for 10 minutes."
            
            payload = {
                "message": message,
                "to": phone_number,
                "sender_id": getattr(settings, 'smsto_sender_id', 'Wellness'),
            }
            
            headers = {
                "Authorization": f"Bearer {settings.smsto_api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                SMSService.BASE_URL,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "OTP sent successfully",
                    "data": response.json()
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to send OTP: {response.text}",
                    "status_code": response.status_code
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "message": "SMS service timeout. Please try again."
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"SMS service error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}"
            }


sms_service = SMSService()
