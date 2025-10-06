import firebase_admin
from firebase_admin import credentials, messaging
import os
from typing import List, Dict, Any, Optional
from fastapi import HTTPException

# Initialize Firebase Admin SDK
cred_path = os.path.join(os.getcwd(), "wellness_service_account_key.json")
try:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Firebase initialization error: {str(e)}")


class FirebaseNotificationService:
    @staticmethod
    def send_notification(token: str, title: str, body: str, data: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Send a notification to a single device using FCM token
        
        Args:
            token: FCM token of the device
            title: Notification title
            body: Notification body
            data: Additional data to send with the notification
            
        Returns:
            Response from FCM
        """
        print(f"🔥 FIREBASE_SERVICE: Starting notification send")
        print(f"📱 Token: {token[:20]}...")
        print(f"📝 Title: {title}")
        print(f"📄 Body: {body}")
        print(f"📦 Data keys: {list(data.keys()) if data else 'None'}")
        
        try:
            print(f"🛠️ FIREBASE_SERVICE: Creating FCM message...")
            # Create message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=token,
            )
            
            print(f"🚀 FIREBASE_SERVICE: Sending message via FCM...")
            # Send message
            response = messaging.send(message)
            print(f"✅ FIREBASE_SERVICE: Successfully sent notification! Message ID: {response}")
            return {"success": True, "message_id": response}
        except Exception as e:
            print(f"❌ FIREBASE_SERVICE: Error sending notification: {str(e)}")
            print(f"🔍 FIREBASE_SERVICE: Exception type: {type(e).__name__}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def send_multicast_notification(tokens: List[str], title: str, body: str, data: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Send a notification to multiple devices using FCM tokens
        
        Args:
            tokens: List of FCM tokens
            title: Notification title
            body: Notification body
            data: Additional data to send with the notification
            
        Returns:
            Response from FCM with success and failure counts
        """
        if not tokens:
            return {"success": False, "error": "No tokens provided"}
            
        try:
            # Create multicast message
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                tokens=tokens,
            )
            
            # Send multicast message
            response = messaging.send_multicast(message)
            
            return {
                "success": True,
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "responses": [r.success for r in response.responses]
            }
        except Exception as e:
            print(f"Error sending multicast notification: {str(e)}")
            return {"success": False, "error": str(e)}


# Create a global instance
firebase_notification_service = FirebaseNotificationService()
