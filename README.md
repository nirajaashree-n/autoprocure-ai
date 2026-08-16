# autoprocure-ai
### An AI procurement agent that turns a simple Slack request into an end-to-end vendor quoting workflow.

Built with Caspian's dual-channel capabilities, autoprocure-ai uses Google Gemini to understand procurement requests, generate vendor communications, and extract quote data from emails and PDF quotations. The application structures the extracted information in SQLite and delivers procurement updates back to managers through Slack.

## 🎥 Demo

<https://drive.google.com/file/d/18LSEiqK96AoOn4kUwTo_JimqEsuMCxHE/view?usp=drive_web>

The demo showcases the complete workflow, from a manager requesting quotations through Slack to vendor communication, AI-powered quote extraction, and procurement status retrieval.

## How It Works

### Quote Request <br>
##### Manager → Slack → Application → Gemini → Application → Caspian → Email → Vendor <br>
1. The manager submits a natural-language procurement request through Slack.
2. The application uses Gemini to extract the intent and relevant requirements.
3. The application retrieves the relevant vendors from SQLite.
4. Gemini generates the quote-request email.
5. The application passes the communication to Caspian, which delivers it to the vendor through email.

### Quote Processing <br>
##### Vendor → Email → Caspian → Application → Gemini → Application → SQLite <br>
1. The vendor responds through email, potentially including a PDF quotation.
2. Caspian receives the response and passes it to the application.
3. Gemini extracts structured information from the response and/or PDF.
4. The application processes the extracted information.
5. The resulting quote is stored in SQLite.

### Status Updates <br>
##### Manager → Slack → Application → Gemini → Application → SQLite → Application → Caspian → Slack <br>
1. The manager asks for a procurement update through Slack.
2. Gemini interprets the request.
3. The application retrieves the relevant quote data from SQLite.
4. The application formats the results.
5. Caspian delivers the response back to the manager through Slack.

## Architecture

                         ┌──────────────┐
                         │    Manager   │
                         └──────┬───────┘
                                │
                              Slack
                                │
                                ▼
                    ┌──────────────────────┐
                    │   autoprocure-ai     │
                    │   Python Application │
                    └───┬──────┬──────┬────┘
                        │      │      │
                        ▼      ▼      ▼
                     Gemini  SQLite  Caspian
                                       │
                                     Email
                                       │
                                       ▼
                                    Vendors
                                       │
                                     Email
                                       │
                                       ▼
                                    Caspian
                                       │
                                       ▼
                              autoprocure-ai

## Multi-Channel Architecture
autoprocure-ai uses Caspian to bridge two communication channels with different roles: <br>

### Channel	Purpose
Slack	Manager ↔ Application <br>
Email	Application ↔ Vendors <br>
The manager stays in Slack while vendors continue using email. Caspian provides the communication layer connecting both sides of the workflow.

## Tech Stack
1. Python — Core application logic
2. Caspian SDK — Multi-channel communication
3. Google Gemini — Intent processing, email generation, and quote/PDF extraction
4. Slack — Manager-facing interface
5. Email — Vendor communication
6. SQLite / Python `sqlite3` — Database storage and interaction
7. DB Browser for SQLite — Database inspection and management
8. python-dotenv — Environment configuration

## Database

The application currently uses two SQLite tables.

#### vendors
vendor_id <br>
name <br>
email <br>

##### quotes
quote_id <br>
vendor_id <br>
item <br>
price <br>
suggestion <br>
confidence <br>
status <br>
email_link <br>

## Current Features
- Natural-language procurement requests
- AI-based intent extraction
- Vendor lookup from SQLite
- AI-generated quote-request emails
- Dual-channel communication through Caspian
- Vendor email response processing
- PDF quotation extraction using Gemini
- Structured quote storage
- Procurement status updates through Slack

## Future Directions
- Automated quote comparison and ranking
- Smarter vendor recommendations
- Automated price negotiation
- Slack-based approval workflows
- Historical vendor and pricing intelligence
- Support for broader procurement workflows

## Setup
### Requirements
Python 3.12 <br>
Caspian SDK API key <br>
Google Gemini API key <br>
Slack app token <br>
Slack bot token <br>

#### 1. Install dependencies

`pip install -r requirements.txt`

#### 2. Initialize the database

The SQLite database is not included in the repository. <br>
Run the database initialization script to create inventory.db and the required tables:

`python db_manager.py`

#### 3. Configure environment variables

Create a .env file containing the following:

```text
GEMINI_API_KEY=your_key
SLACK_APP_TOKEN=your_token
SLACK_BOT_TOKEN=your_token
CASPIAN_API_KEY=your_key
```
#### 4. Run the application

`python app.py`

Never commit your .env file or API keys.

## Built for the Caspian Hackathon

autoprocure-ai explores how multi-channel AI agents can automate real business workflows, using procurement as a practical example.

#### The manager asks. The application coordinates. Vendors respond. AI processes the information. The manager gets the result.
