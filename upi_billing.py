"""
UPI QR Code Generator & GST Billing Engine
"""
import os
import qrcode
import urllib.parse
from PIL import Image, ImageDraw, ImageFont
import config

class UPIBillingEngine:
    def __init__(self, output_dir=config.OUTPUT_DIR):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_upi_string(self, vpa, amount, business_name, invoice_id):
        """Generates standard NPCI compliant UPI Deep Link URI."""
        pn_encoded = urllib.parse.quote(business_name)
        tn_encoded = urllib.parse.quote(f"Invoice {invoice_id}")
        upi_url = f"upi://pay?pa={vpa}&pn={pn_encoded}&am={amount:.2f}&cu=INR&tn={tn_encoded}"
        return upi_url

    def create_upi_qr_code(self, vpa, amount, business_name, invoice_id):
        """
        Creates a valid QR Code PNG image for GPay, PhonePe, Paytm, BHIM.
        Saves image to output directory and returns file path & UPI URI.
        """
        upi_uri = self.generate_upi_string(vpa, amount, business_name, invoice_id)

        # Generate QR Code Matrix
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(upi_uri)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        # Save image
        filename = f"invoice_{invoice_id}_qr.png"
        filepath = os.path.join(self.output_dir, filename)
        qr_img.save(filepath)

        return filepath, upi_uri

    def format_whatsapp_invoice_text(self, invoice_id, customer_name, item_summary, amount, tax, total, vpa, upi_uri):
        """Formats a clean, professional WhatsApp text invoice with payment deep link."""
        text = (
            f"📄 *OFFICIAL GST INVOICE - {config.DEFAULT_BUSINESS['name']}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *Customer*: {customer_name}\n"
            f"🧾 *Invoice No*: `{invoice_id}`\n"
            f"📅 *Date*: {config.DEFAULT_BUSINESS['name']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"📦 *Item Details*:\n{item_summary}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"💵 *Subtotal*: ₹{amount:.2f}\n"
            f"🏛️ *GST (18%)*: ₹{tax:.2f}\n"
            f"💰 *TOTAL DUE*: *₹{total:.2f}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"💳 *HOW TO PAY INSTANTLY VIA UPI*:\n"
            f"1️⃣ Open GPay / PhonePe / Paytm\n"
            f"2️⃣ Scan the QR Code attached OR click the UPI payment link below:\n\n"
            f"📲 *UPI Payment Link*:\n{upi_uri}\n\n"
            f"🆔 *UPI ID / VPA*: `{vpa}`\n\n"
            f"Reply *PAID* after completing payment to receive instant confirmation!"
        )
        return text

    def format_payment_reminder(self, invoice_id, customer_name, amount, upi_uri):
        """Formats polite automated payment reminder for overdue invoices."""
        text = (
            f"🔔 *GENTLE PAYMENT REMINDER*\n\n"
            f"Hi {customer_name},\n"
            f"This is a friendly reminder regarding your pending invoice *#{invoice_id}* for *₹{amount:.2f}*.\n\n"
            f"Tap the link below to clear your payment via GPay / PhonePe / Paytm:\n"
            f"📲 {upi_uri}\n\n"
            f"Thank you for your business! 🙏"
        )
        return text
