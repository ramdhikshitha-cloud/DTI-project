# alert_module.py
import tkinter as tk
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -------- EMAIL CONFIGURATION --------
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "ramdhikshitha@gmail.com"
EMAIL_PASSWORD = "qpcg rscv wilq hyml" 

def send_email_alert(subject, message):
    """Handles the background email transmission."""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS 
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("SUCCESS: Email alert sent.") 
    except Exception as e:
        print("ERROR: Failed to send email:", str(e))

def show_alert_popup(root, accident_text):
    response_received = {"value": False}
    popup = tk.Toplevel(root)
    popup.title("Accident Alert")
    
    # --- DYNAMIC SCREEN CENTERING ---
    width, height = 350, 200
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    popup.geometry(f"{width}x{height}+{x}+{y}")
    
    popup.attributes("-topmost", True) # Force window to the front
    popup.focus_force()               # Grab keyboard focus immediately

    label = tk.Label(popup, 
                     text=f"DETECTED: {accident_text}\n\nPress '1' if you are SAFE", 
                     font=("Arial", 12, "bold"), fg="red")
    label.pack(pady=40)

    def on_safe(event=None):
        """Triggers immediately on '1' key press."""
        if not response_received["value"]:
            response_received["value"] = True
            
            # 1. Close the window INSTANTLY
            popup.destroy() 
            
            # 2. Then process the email in the background
            send_email_alert(
                subject="Accident Notification - Person SAFE",
                message=f"Status: {accident_text}. User confirmed they are safe."
            )

    # Bind the '1' key to the function
    popup.bind("1", on_safe)

    def timeout():
        """Triggered if 10 seconds pass without input."""
        if not response_received["value"]:
            response_received["value"] = True
            if popup.winfo_exists():
                popup.destroy()
                
            send_email_alert(
                subject="URGENT: Accident - No Response",
                message=f"ALERT: {accident_text} detected! No response within 10 seconds."
            )

    # 10000ms = 10 second countdown
    popup.after(10000, timeout)