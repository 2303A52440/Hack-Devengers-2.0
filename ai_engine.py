"""
AI Conversation Engine & Intent Classifier for Indian Businesses
"""
import re
import random
import datetime
from sqlalchemy.orm import Session
from database import ProductCatalog, CustomerLead, ChatMessage, Invoice, Business
from upi_billing import UPIBillingEngine
from voice_processor import VoiceAudioProcessor

class AIAgentEngine:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.billing = UPIBillingEngine()
        self.voice_processor = VoiceAudioProcessor()
        self.business = self.db.query(Business).first()

    def process_message(self, customer_phone: str, user_text: str, is_voice: bool = False):
        """
        Main AI pipeline: Logs message, classifies intent, queries DB knowledge base,
        calculates sentiment, and generates context-aware WhatsApp response.
        """
        # Handle voice note transcription if flagged
        if is_voice:
            voice_res = self.voice_processor.process_audio(raw_transcript=user_text)
            user_text = voice_res["transcript"]

        user_text_lower = user_text.lower().strip()

        # Fetch or Create Customer Lead
        lead = self.db.query(CustomerLead).filter(CustomerLead.phone == customer_phone).first()
        if not lead:
            lead = CustomerLead(phone=customer_phone, name="Valued Customer", status="NEW")
            self.db.add(lead)
            self.db.commit()

        # Update last interaction timestamp
        lead.last_interaction = datetime.datetime.utcnow()

        # Calculate basic sentiment score (-1.0 to +1.0)
        sentiment_score = self._analyze_sentiment(user_text_lower)

        # Log inbound message
        inbound_msg = ChatMessage(
            phone=customer_phone,
            direction="INBOUND",
            message_text=f"[VOICE NOTE] {user_text}" if is_voice else user_text
        )
        self.db.add(inbound_msg)
        self.db.commit()

        # Classify Intent & Generate Response
        intent, response_text, attachment = self._route_intent(lead, user_text, user_text_lower)

        # Log outbound response
        outbound_msg = ChatMessage(phone=customer_phone, direction="OUTBOUND", message_text=response_text, intent=intent)
        self.db.add(outbound_msg)

        lead.status = intent
        self.db.commit()

        return {
            "intent": intent,
            "response_text": response_text,
            "attachment": attachment,
            "sentiment": sentiment_score,
            "is_voice": is_voice,
            "transcript": user_text
        }

    def _analyze_sentiment(self, text: str) -> float:
        positive_words = ["great", "good", "excellent", "love", "buy", "enroll", "paid", "thanks", "thank", "awesome"]
        negative_words = ["bad", "scam", "costly", "expensive", "issue", "fake", "delay", "cancel"]
        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)
        if pos_count > neg_count:
            return 0.8
        elif neg_count > pos_count:
            return -0.6
        return 0.1


    def _route_intent(self, lead: CustomerLead, raw_text: str, text: str):
        """Internal router classifying user intent."""
        
        # 1. Payment Confirmation Intent
        if any(w in text for w in ["paid", "done", "payment done", "sent money", "pay kar diya", "hogaya"]):
            # Check for pending invoice
            pending_inv = self.db.query(Invoice).filter(
                Invoice.customer_phone == lead.phone,
                Invoice.status == "PENDING"
            ).order_by(Invoice.created_at.desc()).first()

            if pending_inv:
                pending_inv.status = "PAID"
                lead.total_spend += pending_inv.total_amount
                self.db.commit()

                reply = (
                    f"🎉 *PAYMENT RECEIVED & VERIFIED!*\n\n"
                    f"Thank you {lead.name}! We have received your payment of *₹{pending_inv.total_amount:.2f}* for Invoice *#{pending_inv.id}*.\n\n"
                    f"✅ Your seat/enrollment is officially confirmed!\n"
                    f"📞 Our team will contact you shortly on this number with login details.\n\n"
                    f"Have a great day! 🙏"
                )
                return "CONVERTED", reply, None
            else:
                reply = "Thank you! We have logged your message. Our team will verify and update your receipt shortly."
                return "PAYMENT_INQUIRY", reply, None

        # 2. Buy / Order Intent
        if any(w in text for w in ["enroll", "buy", "join", "pay now", "admission", "chahiye", "send payment link", "register"]):
            # Find matching product
            products = self.db.query(ProductCatalog).all()
            selected_product = None
            for prod in products:
                if prod.name.lower() in text or any(k in text for k in prod.keywords.split(",")):
                    selected_product = prod
                    break
            
            if not selected_product:
                selected_product = products[0] # Default to first catalog item

            # Generate Invoice & UPI QR
            inv_id = f"INV{random.randint(10000, 99999)}"
            tax = selected_product.price * 0.18
            total = selected_product.price + tax

            qr_path, upi_uri = self.billing.create_upi_qr_code(
                vpa=self.business.upi_vpa if self.business else "apex@upi",
                amount=total,
                business_name=self.business.name if self.business else "Apex Academy",
                invoice_id=inv_id
            )

            # Store Invoice in DB
            invoice = Invoice(
                id=inv_id,
                customer_phone=lead.phone,
                customer_name=lead.name,
                item_summary=f"1x {selected_product.name}",
                amount=selected_product.price,
                tax_amount=tax,
                total_amount=total,
                status="PENDING",
                upi_qr_path=qr_path
            )
            self.db.add(invoice)
            self.db.commit()

            invoice_text = self.billing.format_whatsapp_invoice_text(
                invoice_id=inv_id,
                customer_name=lead.name,
                item_summary=f"1x {selected_product.name}",
                amount=selected_product.price,
                tax=tax,
                total=total,
                vpa=self.business.upi_vpa if self.business else "apex@upi",
                upi_uri=upi_uri
            )
            return "INVOICED", invoice_text, qr_path

        # 3. Product / Pricing Inquiry
        if any(w in text for w in ["price", "fee", "cost", "course", "subject", "details", "batch", "syllabus", "kya hai"]):
            products = self.db.query(ProductCatalog).all()
            catalog_text = f"📚 *{self.business.name if self.business else 'Apex Academy'} - COURSES & PRICING*\n"
            catalog_text += "━━━━━━━━━━━━━━━━━━━━━\n"
            for p in products:
                catalog_text += f"🔹 *{p.name}*\n  • {p.description}\n  • Fee: *₹{p.price:,.0f}* (+18% GST)\n\n"
            catalog_text += "━━━━━━━━━━━━━━━━━━━━━\n"
            catalog_text += "💡 *To enroll now*, simply reply with the course name or type *ENROLL*!"
            return "INQUIRING", catalog_text, None

        # 4. Greeting
        if any(w in text for w in ["hi", "hello", "hey", "namaste", "good morning", "start"]):
            reply = (
                f"👋 *Namaste! Welcome to {self.business.name if self.business else 'Apex Academy'} AI Assistant.*\n\n"
                f"How can I assist you today?\n"
                f"1️⃣ Reply *COURSES* to see our available programs & fees.\n"
                f"2️⃣ Reply *ENROLL* to get instant UPI payment link.\n"
                f"3️⃣ Reply *LOCATION* for our academy address & contact.\n\n"
                f"💬 *You can also ask me any question in Hindi or English!*"
            )
            return "NEW", reply, None

        # 5. Location / Contact Info
        if any(w in text for w in ["location", "address", "where", "contact", "phone", "number"]):
            reply = (
                f"📍 *OUR ADDRESS & CONTACT INFO*\n\n"
                f"🏢 *{self.business.name}*\n"
                f"📍 {self.business.address}\n"
                f"📞 Phone: {self.business.phone}\n"
                f"🌐 Category: {self.business.category}\n\n"
                f"Working Hours: Mon - Sat (9:00 AM - 7:00 PM)"
            )
            return "INFORMATION", reply, None

        # Fallback AI Response
        reply = (
            f"Thank you for contacting *{self.business.name}*!\n\n"
            f"I have received your message: _\"{raw_text}\"_\n\n"
            f"Our course coordinator will connect with you shortly. "
            f"In the meantime, reply *COURSES* to view our programs and pricing."
        )
        return "INQUIRING", reply, None
