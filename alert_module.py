# alert_module.py
import tkinter as tk
import smtplib
import geocoder  # <--- New backend dependency
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -------- EMAIL CONFIGURATION --------
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "ramdhikshitha@gmail.com"
EMAIL_PASSWORD = "qpcg rscv wilq hyml" 

def get_current_location():
    """Backend Logic: Fetches location via IP Address."""
    try:
        g = geocoder.ip('me')
        if g.latlng:
            lat, lng = g.latlng
            city = g.city or "Unknown City"
            # Creates a clickable link for emergency responders
            maps_link = f"https://www.google.com/maps?q={lat},{lng}"
            return f"Location: {city} ({lat}, {lng})\nMap Link: {maps_link}"
        return "Location: Could not determine GPS coordinates."
    except Exception:
        return "Location: Service Unavailable."

def send_email_alert(subject, message):
    """Handles background transmission + Location Data."""
    # Append backend location data to every email
    location_info = get_current_location()
    full_body = f"{message}\n\n--- BACKEND LOG DATA ---\n{location_info}"

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS 
        msg['Subject'] = subject
        msg.attach(MIMEText(full_body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("SUCCESS: Email sent with location data.") 
    except Exception as e:
        print("ERROR: Failed to send email:", str(e))

def show_alert_popup(root, accident_text):
    response_received = {"value": False}
    popup = tk.Toplevel(root)
    popup.title("Accident Alert")
    
    # Center the popup
    w, h = 350, 200
    x = (popup.winfo_screenwidth() // 2) - (w // 2)
    y = (popup.winfo_screenheight() // 2) - (h // 2)
    popup.geometry(f"{w}x{h}+{x}+{y}")
    
    popup.attributes("-topmost", True)
    popup.focus_force()

    label = tk.Label(popup, 
                     text=f"DETECTED: {accident_text}\n\nPress '1' if you are SAFE", 
                     font=("Arial", 12, "bold"), fg="red")
    label.pack(pady=40)

    def on_safe(event=None):
        if not response_received["value"]:
            response_received["value"] = True
            popup.destroy() # Instant UI closure
            send_email_alert(
                subject="Accident Notification - Person SAFE",
                message=f"Status: {accident_text}. User checked in as SAFE."
            )

    popup.bind("1", on_safe)

    def timeout():
        if not response_received["value"]:
            response_received["value"] = True
            if popup.winfo_exists():
                popup.destroy()
            send_email_alert(
                subject="URGENT: Accident - No Response",
                message=f"ALERT: {accident_text} detected! No user response."
            )

    popup.after(10000, timeout)
