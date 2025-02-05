try:
    import requests
except ImportError:
    print("Please install requests: pip install requests")
    exit(1)
import time
import pytest
from unittest.mock import patch

def test_linkedin_automation():
    with patch('subprocess.run') as mock_run:
        # 1. First ensure credentials exist
        credentials_url = "http://127.0.0.1:8000/api/store-credentials"
        credentials_data = {
            "email": "aakashneeli.lm10@gmail.com",
            "password": "Aakash0810&&",
            "user_id": "test_user"
        }
        
        # Store credentials if not already stored
        try:
            response = requests.post(credentials_url, json=credentials_data)
            if response.status_code != 200:
                print("Credential storage failed:", response.text)
                return
        except Exception as e:
            print("Connection error:", str(e))
            return

        # 2. Run LinkedIn automation
        automation_url = "http://127.0.0.1:8000/api/automate/linkedin"
        automation_data = {
            "user_id": "test_user",
            "task_description": "Apply to 3 remote marketing jobs",
            "resume_data": {
                "experience": ["Senior Marketer at ABC Corp (2020-Present)"],
                "skills": ["Digital Marketing", "Campaign Management"],
                "education": ["MBA in Marketing"]
            }
        }

        try:
            # Start automation
            start_time = time.time()
            response = requests.post(automation_url, json=automation_data)
            
            # Print formatted results
            print(f"\n{' Status ':━^40}")
            print(f"► HTTP Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"► Applications Submitted: {result.get('applications', 0)}")
                print(f"► Time Taken: {time.time() - start_time:.2f} seconds")
                
                print(f"\n{' Next Steps ':━^40}")
                print("1. Check browser for automation progress")
                print("2. Verify applications in LinkedIn 'My Jobs'")
                print("3. Review backend/user_creds/test_user.bin")
            else:
                print(f"► Error: {response.text}")

            # New assertions
            mock_run.assert_called_once_with(
                ["python", "backend/playwright_worker.py", "test_user"],
                check=True
            )
            assert response.status_code == 200

        except Exception as e:
            print(f"Automation failed: {str(e)}")

if __name__ == "__main__":
    test_linkedin_automation() 