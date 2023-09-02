import email
import imaplib
from email.header import decode_header

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post('/imap')
async def imap(username: str, password: str):
    imap = imaplib.IMAP4_SSL("outlook.office365.com", 993)

    # Log in
    try:
        imap.login(username, password)
    except imaplib.IMAP4.error:
        return {"message": "Login failed"}

    imap.select("INBOX")

    # Search for mails matching your search criteria
    status, data = imap.search(None, "ALL")

    emails = []
    for mail_id in data[0].split():
        print(f"Fetching mail ID {mail_id.decode('utf-8')}")

        # Fetch the mail
        status, message_data = imap.fetch(mail_id, "(RFC822)")

        # Decode the mail
        msg = email.message_from_bytes(message_data[0][1])

        # Get the subject, sender, and other attributes
        subject = decode_header(msg["Subject"])[0]
        sender = decode_header(msg["From"])[0]
        subject = str(subject[0], subject[1]) if isinstance(subject[0], bytes) else subject[0]
        sender = str(sender[0], sender[1]) if isinstance(sender[0], bytes) else sender[0]

        print(f"Subject: {subject}")
        print(f"From: {sender}")

        # Get the message content
        if msg.is_multipart():
            # Iterate through parts
            for part in msg.walk():
                # Mime type of the part
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                # If plain text, print it
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    body = part.get_payload(decode=True)
                    print(f"Body: {body.decode('utf-8')}")
                    print()
                    emails.append({
                        'subject': subject,
                        'from': sender,
                        'body': body.decode('utf-8')
                    })
        else:
            # If single part message, print the content
            content_type = msg.get_content_type()
            if content_type == "text/plain":
                body = msg.get_payload(decode=True)
                print(f"Body: {body.decode('utf-8')}")
                emails.append({
                    'subject': subject,
                    'from': sender,
                    'body': body.decode('utf-8')
                })
                print()

    imap.close()
    imap.logout()
    return emails
