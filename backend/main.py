import sys
if sys.platform == "win32":
    sys.coinit_flags = 0
    import asyncio
    from asyncio import WindowsSelectorEventLoopPolicy
    asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import playwright.sync_api
from cryptography.fernet import Fernet
import json
import os
from dotenv import load_dotenv
import subprocess
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from multiprocessing import get_context

app = FastAPI()

# Load .env from project root (1 level up from backend/)
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env')) 

# Add validation check
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY not found in .env file")

print(f"Encryption key loaded: {ENCRYPTION_KEY[:4]}...")  # First 4 chars for verification

# Use the environment variable for Fernet
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

# --- Models ---
class LinkedInCredentials(BaseModel):
    email: str
    password: str
    user_id: str  # To associate with encrypted storage

class AutomationRequest(BaseModel):
    user_id: str
    task_description: str  # "Apply to 20 remote marketing jobs"
    resume_data: dict  # { "experience": [...], "skills": [...] }

def _run_playwright(user_id: str):
    """Isolated process for Playwright operations"""
    # MUST BE FIRST IN THE FUNCTION
    import sys
    if sys.platform == "win32":
        sys.coinit_flags = 0
        import asyncio
        from asyncio import WindowsSelectorEventLoopPolicy
        asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=r"C:\Users\Admin\AppData\Local\ms-playwright\chromium-1155\chrome-win\chrome.exe",
            headless=False
        )
        try:
            page = browser.new_page()
            page.goto("https://linkedin.com")
            page.wait_for_timeout(5000)
        finally:
            browser.close()

async def linkedin_automation(user_id: str, task_description: str, resume_data: dict):
    """Run Playwright in isolated process"""
    import subprocess
    subprocess.run([
        "python",
        "backend/playwright_worker.py",
        user_id
    ], check=True)

# --- API Endpoints ---
@app.post("/api/automate/linkedin")
async def automate_linkedin(request: AutomationRequest):
    try:
        result = await linkedin_automation(
            request.user_id, 
            request.task_description, 
            request.resume_data
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/store-credentials")
async def store_credentials(creds: LinkedInCredentials):
    try:
        # Store as JSON instead of colon-separated string
        creds_dict = {
            "email": creds.email,
            "password": creds.password
        }
        encrypted = cipher_suite.encrypt(json.dumps(creds_dict).encode())
        
        with open(f"user_creds/{creds.user_id}.bin", "wb") as f:
            f.write(encrypted)
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))