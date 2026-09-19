"""
Main Application Launcher & CLI Interactive Suite
"""
import os
import sys
import time
import webbrowser
import uvicorn
import config
from database import init_db, SessionLocal, ProductCatalog, CustomerLead, Invoice, Business
from ai_engine import AIAgentEngine

# Ensure Windows stdout handles UTF-8 emojis cleanly
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def print_banner():
    print("==========================================================")
    print("   OMNIFLOW AI - WHATSAPP CRM & UPI BILLING SUITE        ")
    print("==========================================================")
    print(" Features:")
    print("  [+] 24/7 AI WhatsApp Sales Agent (Hindi / English / Hinglish)")
    print("  [+] Instant GPay / PhonePe / Paytm UPI QR Code Generator")
    print("  [+] Official GST Invoice & WhatsApp Text Summaries")
    print("  [+] Automated Payment Reminders & Status Sync")
    print("  [+] Live Web CRM Dashboard & Sandbox")
    print("==========================================================")


def run_server():
    print(f"\n[INFO] Starting FastAPI Web Server at http://{config.HOST}:{config.PORT}...")
    print(f"[INFO] Web Sandbox UI: http://{config.HOST}:{config.PORT}/sandbox\n")
    
    # Auto-open browser after 1.5 seconds
    def open_browser():
        time.sleep(1.5)
        webbrowser.open(f"http://{config.HOST}:{config.PORT}/sandbox")

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    uvicorn.run("app:app", host=config.HOST, port=config.PORT, reload=False)

def run_cli_demo():
    init_db()
    db = SessionLocal()
    ai_engine = AIAgentEngine(db)
    phone = "+919876543210"

    print("\n--- INTERACTIVE TERMINAL CHAT DEMO ---")
    print("Simulating customer chatting on WhatsApp with AI Sales Agent.")
    print("Type your message (or 'exit' to quit):\n")

    while True:
        try:
            user_msg = input("Customer -> ").strip()
            if not user_msg:
                continue
            if user_msg.lower() in ["exit", "quit", "q"]:
                break

            result = ai_engine.process_message(phone, user_msg)
            print(f"\n[AI Agent Response] ({result['intent']}):")
            print(result['response_text'])
            if result.get('attachment'):
                print(f"📷 Attached Scannable UPI QR Image: {result['attachment']}")
            print("-" * 50)
        except (KeyboardInterrupt, EOFError):
            break

    db.close()
    print("\nCLI Demo ended.")

if __name__ == "__main__":
    print_banner()
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        run_cli_demo()
    else:
        run_server()
