import email
import imaplib
from email.header import decode_header

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post('/imap')
async def imap(account: str):
    imap = imaplib.IMAP4_SSL("outlook.office365.com", 993)
    emails = {}
    accounts = account.split(',')
    print(accounts)
    for a in accounts:
        _emails = []
        a = a.strip()
        a = a.split('|')
        if len(a) != 2:
            continue
        username = a[0]
        password = a[1]
        print(username)

        # Log in
        try:
            imap.login(username, password)
        except imaplib.IMAP4.error:
            if username not in emails.keys():
                emails[username] = []
            emails[username].append({
                'subject': 'Login failed',
                'receiver': username,
                'body': 'Login failed',
                'from': ''
            })
            continue

        imap.select("INBOX")

        # Search for mails matching your search criteria
        status, data = imap.search(None, "ALL")

        for mail_id in data[0].split():
            print(f"Fetching mail ID {mail_id.decode('utf-8')}")

            # Fetch the mail
            status, message_data = imap.fetch(mail_id, "(RFC822)")

            # Decode the mail
            msg = email.message_from_bytes(message_data[0][1])

            date_header = msg["Date"]
            date = email.utils.parsedate_to_datetime(date_header)
            date_str = date.strftime("%Y-%m-%d %H:%M:%S")

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
                        _emails.append({
                            'subject': subject,
                            'receiver': username,
                            'from': sender,
                            'body': body.decode('utf-8'),
                            'datetime': date_str
                        })
            else:
                # If single part message, print the content
                content_type = msg.get_content_type()
                if content_type == "text/plain":
                    body = msg.get_payload(decode=True)
                    print(f"Body: {body.decode('utf-8')}")
                    _emails.append({
                        'subject': subject,
                        'receiver': username,
                        'from': sender,
                        'body': body.decode('utf-8'),
                        'datetime': date_str
                    })
                    print()

        _emails = sorted(_emails, key=lambda x: x['datetime'], reverse=True)
        emails[username] = _emails

        imap.close()
        imap.logout()
    return emails
