# autoprocure-ai
### An AI procurement agent that turns a simple Slack request into an end-to-end vendor quoting workflow.

Built with Caspian's dual-channel capabilities, autoprocure-ai uses Google Gemini to understand procurement requests, generate vendor communications, and extract quote data from emails and PDF quotations. The application structures the extracted information in SQLite and delivers procurement updates back to managers through Slack.

## 🎥 Demo

----google drive link here---- enclose in <> brackets

The demo showcases the complete workflow, from a manager requesting quotations through Slack to vendor communication, AI-powered quote extraction, and procurement status retrieval.

## How It Works
### Quote Request

Manager → Slack → Application → Gemini → Application → Caspian → Email → Vendor

The manager submits a natural-language procurement request through Slack.
The application uses Gemini to extract the intent and relevant requirements.
The application retrieves the relevant vendors from SQLite.
Gemini generates the quote-request email.
The application passes the communication to Caspian, which delivers it to the vendor through email.

### Quote Processing

Vendor → Email → Caspian → Application → Gemini → Application → SQLite

The vendor responds through email, potentially including a PDF quotation.
Caspian receives the response and passes it to the application.
Gemini extracts structured information from the response and/or PDF.
The application processes the extracted information.
The resulting quote is stored in SQLite.

### Status Updates

Manager → Slack → Application → Gemini → Application → SQLite → Application → Caspian → Slack

The manager asks for a procurement update through Slack.
Gemini interprets the request.
The application retrieves the relevant quote data from SQLite.
The application formats the results.
Caspian delivers the response back to the manager through Slack.

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

autoprocure-ai uses Caspian to bridge two communication channels with different roles:

### Channel	Purpose
Slack	Manager ↔ Application
Email	Application ↔ Vendors

The manager stays in Slack while vendors continue using email. Caspian provides the communication layer connecting both sides of the workflow.

## Tech Stack
Python — Core application logic
Caspian SDK — Multi-channel communication
Google Gemini — Intent processing, email generation, and quote/PDF extraction
Slack — Manager-facing interface
Email — Vendor communication
SQLite / SQLAlchemy — Data storage and database interaction
python-dotenv — Environment configuration

## Database

The application currently uses two SQLite tables.

#### vendors
vendor_id
name
email

##### quotes
quote_id
vendor_id
item
price
suggestion
confidence
status
email_link

## Current Features
Natural-language procurement requests
AI-based intent extraction
Vendor lookup from SQLite
AI-generated quote-request emails
Dual-channel communication through Caspian
Vendor email response processing
PDF quotation extraction using Gemini
Structured quote storage
Procurement status updates through Slack

## Future Directions
Automated quote comparison and ranking
Smarter vendor recommendations
Automated price negotiation
Slack-based approval workflows
Historical vendor and pricing intelligence
Support for broader procurement workflows

## Setup
### Requirements
Python 3.12
Caspian SDK API key
Google Gemini API key
Slack app token
Slack bot token

#### 1. Install dependencies

`pip install -r requirements.txt`

#### 2. Initialize the database

The SQLite database is not included in the repository.
Run the database initialization script to create inventory.db and the required tables:

`python db_manager.py`

#### 3. Configure environment variables

Create a .env file containing the following:

GEMINI_API_KEY=your_key
SLACK_APP_TOKEN=your_token
SLACK_BOT_TOKEN=your_token
CASPIAN_API_KEY=your_key

#### 4. Run the application

`python app.py`

Never commit your .env file or API keys.

## Built for the Caspian Hackathon

autoprocure-ai explores how multi-channel AI agents can automate real business workflows, using procurement as a practical example.

The manager asks. The application coordinates. Vendors respond. AI processes the information. The manager gets the result.

## Team

[Your Name] · [Partner Name]