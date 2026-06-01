import os
import os.path
import json
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

# Resolve project root relative to this file (admob_core/ -> project root)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(_PROJECT_ROOT / ".env")

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/admob.readonly",
    "https://www.googleapis.com/auth/admob.report",
    "https://www.googleapis.com/auth/admob.monetization",
]

def _resolve_path(env_var: str, default: str) -> str:
    """Resolve a path from env var, making relative paths relative to project root."""
    p = Path(os.getenv(env_var, default))
    if not p.is_absolute():
        p = _PROJECT_ROOT / p
    return str(p)

TOKEN_PATH = _resolve_path("TOKEN_PATH", "token.json")
CREDENTIALS_PATH = _resolve_path("CREDENTIALS_PATH", "credentials.json")

def get_credentials() -> Credentials:
    """
    Loads or refreshes OAuth2 credentials.
    Returns:
        Credentials object.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing access token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(
                    f"Credentials file not found at {CREDENTIALS_PATH}. "
                    "Please download it from the Google Cloud Console."
                )
            
            print("Running interactive OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
            print(f"Credentials saved to {TOKEN_PATH}")

    return creds

if __name__ == "__main__":
    try:
        credentials = get_credentials()
        print("Successfully obtained credentials.")
        print(f"Token expired: {credentials.expired}")
    except Exception as e:
        print(f"Error obtaining credentials: {e}")
