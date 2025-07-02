import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import admin

if __name__ == "__main__":
    # Call delete_account with a dummy username
    # username = "robkhenderson"
    # response = admin.delete_account(username)

    test = "lists"
    try:
        response = admin.create_account(test)
    except Exception as e:
        print(f"Bad request: {e.response.status_code}")  
        if hasattr(e.response.content, 'error'):  
            print(f"Error code: {e.response.content.error}")  
            print(f"Error message: {e.response.content.message}")

    # print("Create account response:", response.message)
