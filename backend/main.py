from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import playwright.sync_api
from cryptography.fernet import Fernet
import json
import os

app = FastAPI()

# Encryption setup
KEY = Fernet.generate_key()  # In prod, store this securely!
cipher_suite = Fernet(KEY)

# --- Models ---
class LinkedInCredentials(BaseModel):
    email: str
    password: str
    user_id: str  # To associate with encrypted storage

class AutomationRequest(BaseModel):
    user_id: str
    task_description: str  # "Apply to 20 remote marketing jobs"
    resume_data: dict  # { "experience": [...], "skills": [...] }

# --- Core Automation Service ---
def linkedin_automation(email: str, password: str, task: str, resume: dict):
    with playwright.sync_api.sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Start visible for debugging
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # Login
            page.goto("https://www.linkedin.com/login")
            page.fill("#username", email)
            page.fill("#password", password)
            page.click("button[type=submit]")
            
            # Job search automation
            page.goto("https://www.linkedin.com/jobs/")
            page.fill(".jobs-search-box__input", "remote marketing manager")
            page.click(".jobs-search-box__submit-button")
            
            # Application logic
            applied = 0
            for _ in range(20):
                page.click(".jobs-search-results__list li:first-child a")
                page.wait_for_selector(".jobs-apply-button", timeout=5000)
                
                if "cover letter" not in page.inner_text(".jobs-application-form"):
                    page.click(".jobs-apply-button")
                    page.fill("#resume-form-experience", json.dumps(resume["experience"]))
                    page.click("button[aria-label='Submit application']")
                    applied += 1
                
                page.click(".artdeco-modal__dismiss")
                
            return {"status": "success", "applications": applied}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            browser.close()

# --- API Endpoints ---
@app.post("/api/automate/linkedin")
async def automate_linkedin(request: AutomationRequest):
    # Get encrypted credentials
    creds_file = f"user_creds/{request.user_id}.bin"
    if not os.path.exists(creds_file):
        raise HTTPException(status_code=400, detail="Credentials not found")
    
    with open(creds_file, "rb") as f:
        decrypted = cipher_suite.decrypt(f.read()).decode()
        creds = json.loads(decrypted)
    
    # Run automation
    result = linkedin_automation(
        email=creds["email"],
        password=creds["password"],
        task=request.task_description,
        resume=request.resume_data
    )
    
    return result

@app.post("/api/store-credentials")
async def store_credentials(creds: LinkedInCredentials):
    # Encrypt and store locally
    os.makedirs("user_creds", exist_ok=True)
    encrypted = cipher_suite.encrypt(json.dumps(creds.dict()).encode())
    
    with open(f"user_creds/{creds.user_id}.bin", "wb") as f:
        f.write(encrypted)
    
    return {"status": "credentials_stored"}