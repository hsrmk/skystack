import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import admin

if __name__ == "__main__":
    # Call delete_account with a dummy username
    username = "noahpinion"
    response = admin.delete_account(username)
    print("Delete account response:", response)
