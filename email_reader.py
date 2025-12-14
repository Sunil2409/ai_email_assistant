import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import html as _html_unescape

# Gmail Configuration
EMAIL_ACCOUNT = "sk7962544@gmail.com"
APP_PASSWORD = "gghzembbhzezwxje"
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993

def decode_bytes(payload, charset):
    """Return a decoded string for a bytes payload.

    Tries the declared charset first, then a few common fallbacks.
    Uses 'replace' on errors so we don't silently lose content and we
    get a usable string even for odd encodings.
    """
    if payload is None:
        return ""
    if isinstance(payload, str):
        return payload

    # Try declared charset first
    tried = []
    if charset:
        try:
            return payload.decode(charset, errors="replace")
        except Exception:
            tried.append(charset)

    # Try common encodings
    for enc in ("utf-8", "cp1252", "latin1"):
        if enc in tried:
            continue
        try:
            return payload.decode(enc, errors="replace")
        except Exception:
            continue

    # Last resort: decode with utf-8 replacing errors
    try:
        return payload.decode("utf-8", errors="replace")
    except Exception:
        return str(payload)

def extract_email_body(msg):
    """Extract clean text from an email message.

    Preference: if a plain text part exists, return it. Otherwise, extract
    text from HTML safely (strip tags and unescape entities).
    """
    plain_text = None
    html_text = None

    if msg.is_multipart():
        for part in msg.walk():
            # Skip container/multipart parts
            if part.get_content_maintype() == "multipart":
                continue

            content_type = part.get_content_type()
            content_disposition = part.get("Content-Disposition") or ""
            charset = part.get_content_charset()

            # Skip attachments
            if isinstance(content_disposition, str) and "attachment" in content_disposition.lower():
                continue

            payload = part.get_payload(decode=True)
            if not payload:
                continue

            if content_type == "text/plain":
                plain_text = decode_bytes(payload, charset)

            elif content_type == "text/html":
                html = decode_bytes(payload, charset)
                soup = BeautifulSoup(html, "html.parser")
                # get_text strips tags; unescape HTML entities
                extracted = soup.get_text(separator="\n", strip=True)
                html_text = _html_unescape.unescape(extracted)

            # If we have both, prefer plain text
            if plain_text:
                return plain_text

        # If no plain text, return HTML-derived text if any
        return html_text or ""

    else:
        payload = msg.get_payload(decode=True)
        charset = msg.get_content_charset()
        text = decode_bytes(payload, charset)
        # If a single-part message looks like HTML, try to extract text
        if text and ("<html" in text.lower() or "<body" in text.lower()):
            soup = BeautifulSoup(text, "html.parser")
            return _html_unescape.unescape(soup.get_text(separator="\n", strip=True))
        return text or ""

try:
    print("Connecting to Gmail...")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL_ACCOUNT, APP_PASSWORD)
    mail.select("inbox")
    print("Connected and Inbox Selected.\n")

    status, messages = mail.search(None, "UNSEEN")
    email_ids = messages[0].split()
    print(f"Unread emails Found: {len(email_ids)}\n")

    if not email_ids:
        print("No unread emails to process.")
    else:
        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Decode sender
            sender = msg.get("From")

            # Decode subject
            subject, encoding = decode_header(msg.get("Subject"))[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8", errors="ignore")

            print("From   :", sender)
            print("Subject:", subject)
            print("-" * 50)

            # Extract body
            body = extract_email_body(msg)
            print("\nBody:\n", body)
            print("=" * 60)

    mail.logout()
    print("Connection Closed Cleanly")

except imaplib.IMAP4.error as e:
    print("IMAP error occurred:", e)
except Exception as e:
    print("Unexpected error:", e)
