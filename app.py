"""
FastAPI Server & Web Interactive Sandbox for AI WhatsApp CRM
"""
import os
import config
from fastapi import FastAPI, Request, Query, Response, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import init_db, SessionLocal, CustomerLead, ChatMessage, Invoice, ProductCatalog, Business
from ai_engine import AIAgentEngine
from whatsapp_service import WhatsAppService

# Initialize Database
init_db()

app = FastAPI(
    title="AI WhatsApp Business CRM & UPI Billing Engine",
    description="Automated Sales Agent, UPI QR Generator, and CRM Suite for Indian MSMEs",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
wa_service = WhatsAppService()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request Models
class SimulateChatRequest(BaseModel):
    phone: str = "+919876543210"
    message: str
    is_voice: bool = False

class ProductCreateRequest(BaseModel):
    name: str
    description: str
    price: float
    category: str = "Coaching"
    keywords: str = ""

@app.get("/")
def home():
    return {
        "status": "online",
        "app": "OmniFlow AI - WhatsApp CRM & UPI Billing Engine",
        "version": "2.0.0",
        "dashboard": f"http://{config.HOST}:{config.PORT}/dashboard",
        "interactive_sandbox": f"http://{config.HOST}:{config.PORT}/sandbox",
        "docs": f"http://{config.HOST}:{config.PORT}/docs"
    }

@app.get("/dashboard", response_class=FileResponse)
def get_dashboard_ui():
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    raise HTTPException(status_code=404, detail="Dashboard UI file not found")

# 1. Meta Webhook Handlers
@app.get("/webhook/whatsapp")
def verify_whatsapp_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    challenge = wa_service.verify_webhook(hub_mode, hub_verify_token, hub_challenge)
    if challenge:
        return Response(content=str(challenge), media_type="text/plain")
    raise HTTPException(status_code=403, detail="Invalid verification token")

@app.post("/webhook/whatsapp")
async def receive_whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    extracted = wa_service.parse_incoming_webhook(payload)
    
    if extracted:
        ai_engine = AIAgentEngine(db)
        result = ai_engine.process_message(extracted["phone"], extracted["message"])
        wa_service.send_text_message(extracted["phone"], result["response_text"])
    
    return {"status": "success"}

# 2. Interactive Sandbox Chat Endpoint
@app.post("/api/simulate_chat")
def simulate_chat(data: SimulateChatRequest, db: Session = Depends(get_db)):
    ai_engine = AIAgentEngine(db)
    result = ai_engine.process_message(data.phone, data.message, is_voice=data.is_voice)
    return result


# 3. CRM Leads API
@app.get("/api/leads")
def get_leads(db: Session = Depends(get_db)):
    leads = db.query(CustomerLead).order_by(CustomerLead.last_interaction.desc()).all()
    return leads

# 4. Invoices API
@app.get("/api/invoices")
def get_invoices(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).all()
    return invoices

@app.post("/api/invoice/reminder/{invoice_id}")
def send_payment_reminder(invoice_id: str, db: Session = Depends(get_db)):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    biz = db.query(Business).first()
    vpa = biz.upi_vpa if biz else "apex@upi"
    upi_uri = f"upi://pay?pa={vpa}&am={inv.total_amount:.2f}&tn=Invoice%20{inv.id}"
    
    reminder_text = wa_service.billing.format_payment_reminder(
        invoice_id=inv.id,
        customer_name=inv.customer_name or "Customer",
        amount=inv.total_amount,
        upi_uri=upi_uri
    )
    
    wa_service.send_text_message(inv.customer_phone, reminder_text)
    return {"status": "sent", "reminder_text": reminder_text}

# 5. Serve QR Code Files
@app.get("/output/{filename}")
def serve_output_file(filename: str):
    file_path = os.path.join(config.OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

# 6. Interactive Web Sandbox UI
@app.get("/sandbox", response_class=HTMLResponse)
def get_sandbox_ui():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>AI WhatsApp Agent & CRM Sandbox</title>
        <style>
            * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            body { background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
            .container { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 380px 1fr; gap: 20px; height: 90vh; }
            .panel { background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; display: flex; flex-direction: column; }
            h2 { margin-top: 0; color: #38bdf8; font-size: 1.2rem; border-bottom: 1px solid #334155; padding-bottom: 10px; }
            .chat-messages { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; padding-right: 8px; }
            .msg { max-width: 85%; padding: 12px 16px; border-radius: 12px; font-size: 0.92rem; line-height: 1.4; white-space: pre-wrap; }
            .user-msg { align-self: flex-end; background: #0284c7; color: white; border-bottom-right-radius: 2px; }
            .bot-msg { align-self: flex-start; background: #334155; color: #f8fafc; border-bottom-left-radius: 2px; }
            .qr-preview { max-width: 180px; margin-top: 10px; border-radius: 8px; border: 2px solid #38bdf8; }
            .input-group { display: flex; gap: 8px; margin-top: 15px; }
            input[type="text"] { flex: 1; padding: 12px; border-radius: 8px; border: 1px solid #475569; background: #0f172a; color: white; outline: none; }
            button { background: #0284c7; color: white; border: none; padding: 12px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; }
            button:hover { background: #0369a1; }
            .table-view { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.85rem; }
            .table-view th, .table-view td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #334155; }
            .table-view th { color: #94a3b8; }
            .badge { padding: 4px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
            .badge-PAID { background: #059669; color: white; }
            .badge-PENDING { background: #d97706; color: white; }
            .badge-NEW { background: #2563eb; color: white; }
        </style>
    </head>
    <body>
        <h1 style="margin: 0 0 15px 0; font-size: 1.5rem; color: #38bdf8;">🟢 AI WhatsApp Agent & UPI CRM Sandbox</h1>
        <div class="container">
            <!-- Left Chat Panel -->
            <div class="panel">
                <h2>📱 Live WhatsApp Simulator</h2>
                <div class="chat-messages" id="chatBox">
                    <div class="msg bot-msg">👋 Namaste! Welcome to Apex Academy AI Assistant. Type <b>Hi</b> or ask a question!</div>
                </div>
                <div class="input-group">
                    <input type="text" id="userInput" placeholder="Type message (e.g. 'fees', 'enroll', 'paid')..." onkeypress="if(event.key==='Enter') sendMessage()">
                    <button onclick="sendMessage()">Send</button>
                </div>
            </div>

            <!-- Right Analytics Dashboard -->
            <div class="panel" style="overflow-y: auto;">
                <h2>📊 Live CRM Leads & Generated UPI Invoices</h2>
                <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                    <button onclick="loadDashboard()" style="background: #334155;">🔄 Refresh Data</button>
                </div>

                <h3 style="font-size: 1rem; color: #f59e0b;">🧾 Generated Invoices</h3>
                <table class="table-view" id="invoiceTable">
                    <thead>
                        <tr><th>Inv ID</th><th>Customer</th><th>Amount</th><th>Status</th><th>Action</th></tr>
                    </thead>
                    <tbody></tbody>
                </table>

                <h3 style="font-size: 1rem; color: #38bdf8; margin-top: 25px;">👥 Customer Leads</h3>
                <table class="table-view" id="leadTable">
                    <thead>
                        <tr><th>Phone</th><th>Name</th><th>Status</th><th>Spend</th></tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>

        <script>
            const phone = "+919876543210";

            async function sendMessage() {
                const input = document.getElementById("userInput");
                const text = input.value.trim();
                if (!text) return;

                const chatBox = document.getElementById("chatBox");
                chatBox.innerHTML += `<div class="msg user-msg">${text}</div>`;
                input.value = "";
                chatBox.scrollTop = chatBox.scrollHeight;

                try {
                    const res = await fetch("/api/simulate_chat", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ phone: phone, message: text })
                    });
                    const data = await res.json();

                    let botHtml = `<div class="msg bot-msg">${data.response_text}</div>`;
                    if (data.attachment) {
                        const filename = data.attachment.split(/[\\\\/]/).pop();
                        botHtml += `<div class="msg bot-msg"><img class="qr-preview" src="/output/${filename}" alt="UPI QR Code"><br><small>📷 Scannable GPay/PhonePe UPI QR Code</small></div>`;
                    }
                    chatBox.innerHTML += botHtml;
                    chatBox.scrollTop = chatBox.scrollHeight;

                    loadDashboard();
                } catch (e) {
                    console.error(e);
                }
            }

            async function loadDashboard() {
                try {
                    // Load Invoices
                    const invRes = await fetch("/api/invoices");
                    const invoices = await invRes.json();
                    const invTbody = document.querySelector("#invoiceTable tbody");
                    invTbody.innerHTML = invoices.map(i => `
                        <tr>
                            <td><b>#${i.id}</b></td>
                            <td>${i.customer_name || i.customer_phone}</td>
                            <td>₹${i.total_amount.toFixed(2)}</td>
                            <td><span class="badge badge-${i.status}">${i.status}</span></td>
                            <td>${i.status === 'PENDING' ? `<button onclick="sendReminder('${i.id}')" style="padding:4px 8px; font-size:0.75rem;">🔔 Remind</button>` : '✅ Paid'}</td>
                        </tr>
                    `).join("");

                    // Load Leads
                    const leadRes = await fetch("/api/leads");
                    const leads = await leadRes.json();
                    const leadTbody = document.querySelector("#leadTable tbody");
                    leadTbody.innerHTML = leads.map(l => `
                        <tr>
                            <td>${l.phone}</td>
                            <td>${l.name}</td>
                            <td><span class="badge badge-${l.status}">${l.status}</span></td>
                            <td>₹${l.total_spend.toFixed(2)}</td>
                        </tr>
                    `).join("");
                } catch (e) {
                    console.error(e);
                }
            }

            sendReminder = async (invId) => {
                await fetch(`/api/invoice/reminder/${invId}`, { method: "POST" });
                alert("Automated WhatsApp Payment Reminder Sent!");
                loadDashboard();
            }

            loadDashboard();
        </script>
    </body>
    </html>
    """
    return html_content
