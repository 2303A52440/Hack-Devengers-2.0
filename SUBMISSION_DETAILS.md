# 📋 Hack Devengers 2.0 — Official Submission Copy

Copy and paste these exact, polished answers directly into the **Hack Devengers 2.0 Project Submission Form**: [Google Form Link](https://forms.gle/eEZdVozFpq35DLvt8)

---

### 1. Project Title
`OmniFlow AI`

### 2. Project Tagline (One Sentence Pitch)
`Autonomous Multimodal WhatsApp CRM & Real-Time UPI Billing Engine for Indian Businesses.`

---

### 3. Problem Statement
Indian small businesses, coaching institutes, and e-commerce vendors face three critical bottlenecks:
1. **High Drop-off Rates:** Leads messaging on WhatsApp go cold because human reps take hours to respond to pricing and course inquiries.
2. **Payment Friction:** Sending manual bank details or generic payment links causes delay. Customers abandon purchase decisions before completing checkout.
3. **Fragmented Lead Tracking:** Customer conversations, invoices, and payment statuses remain scattered across individual phone screens with no centralized CRM.

---

### 4. Proposed Solution
**OmniFlow AI** solves this by automating the entire sales funnel directly inside WhatsApp and Web:
- **Instant Multimodal AI Agent:** Reads incoming text queries and voice notes (supporting English, Hindi, Hinglish, and regional code-switching) to instantly answer catalog, pricing, and location questions.
- **Dynamic NPCI-Compliant UPI QR Invoicing:** Generates itemized GST invoices with custom-generated UPI QR code images and instant pay links (GPay, PhonePe, Paytm, BHIM).
- **Centralized Real-Time CRM Dashboard:** Provides business owners with a live web dashboard tracking lead stages, revenue metrics, sentiment scores, and one-click payment verification.

---

### 5. Technical Architecture & Stack Used
- **Backend:** Python 3.10, FastAPI, Uvicorn
- **Database:** SQLite, SQLAlchemy ORM
- **AI & Intent Engine:** Context-aware keyword router, sentiment analyzer, voice transcript handler
- **Payment Engine:** NPCI UPI URI Specification, `qrcode`, `Pillow` image manipulation
- **Frontend Dashboard:** HTML5, Tailwind CSS, Alpine.js, FontAwesome

---

### 6. Key Features & Highlights
1. **Multimodal Audio Processor:** Handles voice note transcriptions seamlessly.
2. **Automated UPI QR Generation:** Creates unique, scannable QR images with exact invoice totals and merchant VPAs.
3. **Automated Payment Confirmation:** Upgrades lead status to `CONVERTED` upon detecting customer payment confirmations.
4. **Automated Reminders:** One-click automated payment reminders for pending invoices.
5. **Interactive Web Sandbox:** Built-in live WhatsApp simulator for instant testing and demonstration.

---

### 7. Future Roadmap & Scalability
- **Meta WhatsApp Cloud API Integration:** Direct webhooks for live enterprise deployment.
- **Razorpay / Cashfree Webhook Sync:** Automated instant reconciliation upon payment completion.
- **Voice Agent Expansion:** Direct phone call handling via Twilio / Plivo integration.

---

### 8. Repository & Demo Links
- **GitHub Repository Link:** *(Paste your public GitHub repo URL here)*
- **Demo Video Link:** *(Paste your Google Drive / YouTube video link here)*
- **Live Demo / Web Dashboard URL:** `http://127.0.0.1:8000/dashboard` *(or your hosted Vercel/Render URL)*
