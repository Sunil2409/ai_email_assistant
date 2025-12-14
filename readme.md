# AI Email Assistant (Gmail Automation)

A Python-based Gmail automation tool that reads unread emails,
extracts clean text content, classifies them into categories,
and automatically performs actions like starring or moving emails
to folders.

## Features
- Connects to Gmail using IMAP
- Extracts clean email body (HTML → text)
- Classifies emails (Urgent, Work, Personal, Promotional)
- Automatically stars or moves emails
- Uses environment variables for credentials
- Dockerized for easy execution

## Requirements
- Python 3.10+
- Gmail App Password
- Docker (optional)

# To Run the file
In terminal: docker --version 
# -> If not installed:
Mac / Windows: https://www.docker.com/products/docker-desktop

# Run in your IDE
clone this Git or download it →
cd ai-email-assistant

# Create a Gmail App Password (VERY IMPORTANT)
Go to Google Account → Security →
Enable 2-Step Verification →
Create an App Password →
Select: →
App: Mail →
Device: Other →
Copy the generated password (16 characters)
⚠️ Normal Gmail password will NOT work.


# Run the below command inside the project folder
docker build -t ai-email-assistant .

# Run
docker run --rm \
  -e EMAIL_ACCOUNT="your_email@gmail.com" \
  -e APP_PASSWORD="your_gmail_app_password" \
  ai-email-assistant

# Expected Output
Connecting to Gmail...
Connected and Inbox Selected.

Unread emails Found: 3

From     : John Doe
Subject  : Project deadline
Category : WORK
Action taken.

Connection Closed Cleanly
