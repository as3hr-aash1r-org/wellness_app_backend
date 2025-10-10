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
    pass


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
        
        try:
            # Ensure all data values are strings
            string_data = {}
            if data:
                for key, value in data.items():
                    string_data[key] = str(value) if value is not None else ""
            
            print(f"🔥 FIREBASE_SERVICE: Single notification data: {string_data}")
            
            # Create message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=string_data,
                token=token,
            )
            
            # Send message
            response = messaging.send(message)
            return {"success": True, "message_id": response}
        except Exception as e:
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
            # Ensure all data values are strings
            string_data = {}
            if data:
                for key, value in data.items():
                    string_data[key] = str(value) if value is not None else ""
            
            # Ensure all tokens are strings
            string_tokens = [str(token) for token in tokens]
            
            print(f"🔥 FIREBASE_SERVICE: Multicast data: {string_data}")
            print(f"🔥 FIREBASE_SERVICE: Token count: {len(string_tokens)}")
            
            # Create multicast message using send_each_for_multicast (more reliable)
            message = messaging.MulticastMessage(
                data=string_data,
                notification=messaging.Notification(
                    title=str(title),
                    body=str(body)
                ),
                tokens=string_tokens,
            )
            
            # Send multicast message using send_each_for_multicast
            response = messaging.send_each_for_multicast(message)
            
            # Log individual results
            for i, resp in enumerate(response.responses):
                if resp.success:
                    print(f"✅ Notification successfully sent to token {string_tokens[i][:10]}...")
                else:
                    print(f"❌ Failed to send notification to token {string_tokens[i][:10]}...: {resp.exception}")
            
            print(f"📊 FIREBASE_SERVICE: Multicast complete - Success: {response.success_count}, Failed: {response.failure_count}")
            
            return {
                "success": response.success_count > 0,
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "responses": response.responses
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# Create a global instance
firebase_notification_service = FirebaseNotificationService()
