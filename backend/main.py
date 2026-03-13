from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from scanner import MailScanner
import csv
import io

app = FastAPI(title="MailTrace API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

scanner = MailScanner()

@app.get("/")
async def root():
    return {"message": "MailTrace API is running! Visit /docs for the interactive UI."}

@app.get("/scan/{email}")
async def run_email_scan(email: str):
    results = await scanner.scan_all(email)
    return {"email": email, "results": results}

@app.post("/scan-bulk")
async def bulk_scan(file: UploadFile = File(...)):
    content = await file.read()
    decoded = content.decode("utf-8").splitlines()
    reader = csv.reader(decoded)

    emails = []
    for row in reader:
        if not row:
            continue
        cell = row[0].strip()
        # containing "email" or "Email" or "EMAIL")
        if not cell or cell.lower() == "email":
            continue
        emails.append(cell)

    bulk_results = []
    for email in emails:
        result = await scanner.scan_all(email)
        bulk_results.append({"email": email, "data": result})

    return {"total": len(emails), "results": bulk_results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)