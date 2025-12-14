import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import html as _html_unescape

# -------------------------------
# Gmail Configuration
# -------------------------------
EMAIL_ACCOUNT = "sk7962544@gmail.com"
APP_PASSWORD = "gghzembbhzezwxje"

IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993


# -------------------------------
# Utility: Decode bytes safely
# -------------------------------
def decode_bytes(payload, charset):
    if payload is None:
        return ""

    if isinstance(payload, str):
        return payload

    if charset:
        try:
            return payload.decode(charset, errors="replace")
        except Exception:
            pass

    for enc in ("utf-8", "cp1252", "latin1"):
        try:
            return payload.decode(enc, errors="replace")
        except Exception:
            continue

    return payload.decode("utf-8", errors="replace")


# -------------------------------
# Extract clean email body
# -------------------------------
def extract_email_body(msg):
    plain_text = None
    html_text = None

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue

            content_type = part.get_content_type()
            disposition = part.get("Content-Disposition") or ""
            charset = part.get_content_charset()

            if "attachment" in disposition.lower():
                continue

            payload = part.get_payload(decode=True)
            if not payload:
                continue

            if content_type == "text/plain":
                plain_text = decode_bytes(payload, charset)

            elif content_type == "text/html" and not plain_text:
                html = decode_bytes(payload, charset)
                soup = BeautifulSoup(html, "html.parser")
                text = soup.get_text(separator="\n", strip=True)
                html_text = _html_unescape.unescape(text)

            if plain_text:
                return plain_text

        return html_text or ""

    else:
        payload = msg.get_payload(decode=True)
        charset = msg.get_content_charset()
        text = decode_bytes(payload, charset)

        if "<html" in text.lower():
            soup = BeautifulSoup(text, "html.parser")
            return _html_unescape.unescape(
                soup.get_text(separator="\n", strip=True)
            )

        return text


# -------------------------------
# Milestone 6: Classification Rules
# -------------------------------
def classify_email(subject, body):
    text = f"{subject} {body}".lower()

    urgent_keywords = ["urgent", "asap", "immediately", "action required"]
    work_keywords = ["report", "meeting", "deadline", "project", "client"]
    promo_keywords = ["offer", "sale", "discount", "buy now", "unsubscribe"]

    for word in urgent_keywords:
        if word in text:
            return "URGENT"

    for word in work_keywords:
        if word in text:
            return "WORK"

    for word in promo_keywords:
        if word in text:
            return "PROMOTIONAL"

    return "PERSONAL"


# -------------------------------
# Milestone 7: Email Actions
# -------------------------------
def star_email(mail, email_id):
    mail.store(email_id, "+FLAGS", "\\Flagged")


def move_email(mail, email_id, folder):
    mail.copy(email_id, folder)
    mail.store(email_id, "+FLAGS", "\\Deleted")


# -------------------------------
# Main Execution
# -------------------------------
try:
    print("Connecting to Gmail...")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL_ACCOUNT, APP_PASSWORD)
    mail.select("inbox")
    print("Connected and Inbox Selected.\n")

    status, messages = mail.search(None, "UNSEEN")
    email_ids = messages[0].split()

    print(f"Unread emails Found: {len(email_ids)}\n")

    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Decode Subject
        subject, encoding = decode_header(msg.get("Subject"))[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8", errors="ignore")

        sender = msg.get("From")
        body = extract_email_body(msg)

        category = classify_email(subject or "", body or "")

        print("From     :", sender)
        print("Subject  :", subject)
        print("Category :", category)
        print("-" * 50)

        # Automation Actions
        if category == "URGENT":
            star_email(mail, email_id)

        elif category == "WORK":
            move_email(mail, email_id, "Work")

        elif category == "PERSONAL":
            move_email(mail, email_id, "Personal")

        elif category == "PROMOTIONAL":
            move_email(mail, email_id, "Promotions")

        print("Action taken.\n")

    # Permanently remove deleted emails
    mail.expunge()
    mail.logout()
    print("Connection Closed Cleanly")

except imaplib.IMAP4.error as e:
    print("IMAP error occurred:", e)

except Exception as e:
    print("Unexpected error:", e)
