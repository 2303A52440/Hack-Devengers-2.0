"""
AI WhatsApp Business CRM - Configuration & Settings
"""
import os

# Project Base Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Database
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'whatsapp_crm.db')}"

# Default Business Settings (Sample Business: EdTech & Coaching Institute)
DEFAULT_BUSINESS = {
    "name": "Apex EdTech Academy",
    "owner_name": "Seetharam",
    "phone": "+91 98765 43210",
    "category": "Education / Coaching",
    "upi_vpa": "apexcoaching@okicici",
    "gstin": "27AAACA1234B1Z5",
    "address": "MG Road, Bengaluru, Karnataka 560001",
    "currency": "₹"
}

# Meta WhatsApp Business API Credentials (Replace with live token when deploying)
WHATSAPP_API_TOKEN = os.getenv("WHATSAPP_API_TOKEN", "MOCK_META_WHATSAPP_TOKEN_12345")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "109876543210987")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "MY_SECURE_WEBHOOK_TOKEN")

# Server Settings
HOST = "127.0.0.1"
PORT = 8000
