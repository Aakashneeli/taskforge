import requests
import os

def test_full_workflow():
    # 1. Store credentials
    cred_response = requests.post(
        "http://127.0.0.1:8000/api/automate/linkedin",
        json={
            "user_id": "test_user",
            "task_description": "Test automation",
            "resume_data": {}
        }
    )
    
    # 2. Trigger automation
    auto_response = requests.post(
        "http://127.0.0.1:8000/api/automate/linkedin",
        json={
            "user_id": "test_user",
            "task_description": "Test automation",
            "resume_data": {}
        }
    )
    
    # 3. Verify linked outcomes
    assert auto_response.json()['success'] == True
    assert os.path.exists("user_creds/test_user.bin")

print(f"Status Code: {cred_response.status_code}")
print(f"Response Content: {cred_response.text}")
print(f"Status Code: {auto_response.status_code}")
print(f"Response Content: {auto_response.text}") 