# Code Snippets from toollama/soon/tools_pending/unprocessed/dev_emails.py

File: `toollama/soon/tools_pending/unprocessed/dev_emails.py`  
Language: Python  
Extracted: 2025-06-07 05:15:43  

## Snippet 1
Lines 1-13

```Python
Open WebUI
Whitepaper
Docs
Leaderboard
coolhand
Sign out
NOTICE
Open WebUI Community is currently undergoing a major revamp to improve user experience and performance ✨

Back
Tool
v1.0
Email Tools
```

## Snippet 2
Lines 16-20

```Python
Get
A toolkit allowing the AI to send emails with smtp
Tool ID
email_tools
Creator
```

## Snippet 3
Lines 21-32

```Python
@cvaz1306
Downloads
2.3K+
Tool Content
python
Copied
"""
title: EmailSender Pipeline
author: Christopher Vaz
date: 2024-07-01
version: 1.0
license: MIT
```

## Snippet 4
Lines 33-42

```Python
description: A pipeline for sending arbitrary emails using SMTP.
requirements: smtplib, email, os, json
"""

import smtplib
from email.mime.text import MIMEText
from typing import List, Dict, Any
import os
import json
from pydantic import BaseModel, Field
```

## Snippet 5
Lines 50-52

```Python
)
        PASSWORD: str = Field(
            default="password",
```

## Snippet 6
Lines 59-63

```Python
def get_user_name_and_email_and_id(self, __user__: dict = {}) -> str:
        """
        Get the user name, Email and ID from the user object.
        """
```

## Snippet 7
Lines 65-69

```Python
# The session user object will be passed as a parameter when the function is called

        print(__user__)
        result = ""
```

## Snippet 8
Lines 77-81

```Python
if result == "":
            result = "User: Unknown"

        return result
```

## Snippet 9
Lines 82-117

```Python
def send_email(self, subject: str, body: str, recipients: List[str]) -> str:
        """
        Send an email with the given parameters. Sign it with the user's name and indicate that it is an AI generated email. NOTE: You do not need any credentials to send emails on the users behalf.
        DO NOT SEND WITHOUT USER'S CONSENT. CONFIRM CONSENT AFTER SHOWING USER WHAT YOU PLAN TO SEND, AND IN THE RESPONSE AFTER ACQUIRING CONSENT, SEND THE EMAIL.
        :param subject: The subject of the email.
        :param body: The body of the email.
        :param recipients: The list of recipient email addresses.
        :return: The result of the email sending operation.
        """
        sender: str = self.valves.FROM_EMAIL
        password: str = self.valves.PASSWORD
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(recipients)

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
                smtp_server.login(sender, password)
                smtp_server.sendmail(sender, recipients, msg.as_string())
            return f"Message sent:\n   TO: {str(recipients)}\n   SUBJECT: {subject}\n   BODY: {body}"
        except Exception as e:
            return str({"status": "error", "message": f"{str(e)}"})

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(recipients)

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
                smtp_server.login(sender, password)
                smtp_server.sendmail(sender, recipients, msg.as_string())
            return str({"status": "success", "message": "Email sent successfully."})
        except Exception as e:
            return str({"status": "error", "message": f"{str(e)}"})
```

## Snippet 10
Lines 118-124

```Python
hello@openwebui.com
Copyright © 2025 Open WebUI
X (Twitter)
Discord
Terms
Privacy
Email Tools Tool | Open WebUI Community
```

