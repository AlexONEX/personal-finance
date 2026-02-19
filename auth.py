"""auth.py

Shared OAuth authentication for Google Sheets.

First run: opens browser for user consent, saves token.json
Subsequent runs: uses token.json automatically
"""

from pathlib import Path

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def get_gspread_client() -> gspread.Client:
    """Get authenticated gspread client using OAuth.

    First run: opens browser for authorization
    Subsequent runs: uses saved token

    Returns:
        gspread.Client: Authenticated client ready to use

    Raises:
        FileNotFoundError: If credentials.json is missing
    """
    if not Path(CREDENTIALS_FILE).exists():
        raise FileNotFoundError(
            f"{CREDENTIALS_FILE} not found. See OAUTH_SETUP.md for instructions."
        )

    creds = None

    # Load existing token if available
    if Path(TOKEN_FILE).exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no valid credentials, log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired token
            creds.refresh(Request())
        else:
            # Full OAuth flow (opens browser)
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token for future runs
        Path(TOKEN_FILE).write_text(creds.to_json())
        print(f"✓ Token saved to {TOKEN_FILE}")

    return gspread.authorize(creds)
