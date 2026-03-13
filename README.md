#  MailTrace OSINT: Digital Footprint Analyzer

**MailTrace** is a high-performance Open Source Intelligence (OSINT) tool designed to map the digital presence associated with an email address. By leveraging asynchronous API orchestration and public authentication endpoints, MailTrace identifies registered accounts across major platforms like GitHub, Microsoft, Spotify, and more.

![Home Page](public/image.png)

##  Key Features
- **Real-time Account Discovery:** Checks 50+ platforms (Microsoft, GitHub, Adobe, Spotify, etc.) without alerting the target.
- **Identity Enrichment:** Automatically pulls public profile names, bios, and avatars.
- **Asynchronous Engine:** Built with `FastAPI` and `httpx` for non-blocking, parallel site scanning.
- **Bulk Analysis:** Upload a CSV of emails to generate a comprehensive footprint report.
- **Clean UI:** A modern Glassmorphism dashboard built with Tailwind CSS.

##  Tech Stack
- **Backend:** Python 3.10+, FastAPI, `httpx` (Async HTTP requests)
- **Frontend:** HTML5, Tailwind CSS, JavaScript (Fetch API)
- **Logic:** OSINT Search Enumeration & API Integration

##  Project Structure
```text
mailtrace/
├── backend/
│   ├── main.py            # FastAPI routes & Bulk Upload logic
│   ├── scanner.py         # The OSINT engine (Site modules)
│   └── requirements.txt   # Backend dependencies
├── frontend/
│   ├── index.html         # Main Dashboard UI
│   └── script.js          # API Integration & UI Logic
└── README.md