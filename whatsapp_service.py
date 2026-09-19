"""
Meta WhatsApp Business Cloud API Integration Service
Handles Webhooks, Sending Messages, Media Attachments, and Live Simulation
"""
import os
import requests
import config

class WhatsAppService:
    def __init__(self, token=config.WHATSAPP_API_TOKEN, phone_id=config.WHATSAPP_PHONE_ID):
        self.token = token
        self.phone_id = phone_id
        self.api_url = f"https://graph.facebook.com/v18.0/{self.phone_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def verify_webhook(self, mode: str, token: str, challenge: str):
        """Validates Meta Webhook challenge token during initial setup."""
        if mode == "subscribe" and token == config.WHATSAPP_VERIFY_TOKEN:
            return int(challenge)
        return None

    def send_text_message(self, recipient_phone: str, message_text: str):
        """Sends WhatsApp text message via Meta Cloud API or local logger."""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_phone,
            "type": "text",
            "text": {
                "preview_url": True,
                "body": message_text
            }
        }

        # Check if using Live Meta Token or Local Sandbox
        if self.token and "MOCK" not in self.token:
            try:
                resp = requests.post(self.api_url, headers=self.headers, json=payload, timeout=5)
                return resp.json()
            except Exception as e:
                print(f"[API ERROR] Failed to deliver WhatsApp message via Meta: {e}")
                return {"status": "error", "message": str(e)}
        else:
            print(f"\n[WHATSAPP OUTBOUND -> {recipient_phone}]\n{message_text}\n{'='*40}")
            return {"status": "simulated", "recipient": recipient_phone, "message": message_text}

    def parse_incoming_webhook(self, payload: dict):
        """Extracts sender phone number, customer name, and text from Meta Webhook JSON."""
        try:
            entry = payload.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            contacts = value.get("contacts", [])
            messages = value.get("messages", [])

            if not messages:
                return None

            msg = messages[0]
            sender_phone = msg.get("from")
            text_body = ""

            if msg.get("type") == "text":
                text_body = msg.get("text", {}).get("body", "")
            elif msg.get("type") == "interactive":
                text_body = msg.get("interactive", {}).get("button_reply", {}).get("title", "")

            customer_name = contacts[0].get("profile", {}).get("name", "Customer") if contacts else "Customer"

            return {
                "phone": sender_phone,
                "name": customer_name,
                "message": text_body
            }
        except (IndexError, KeyError, AttributeError):
            return None
