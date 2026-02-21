"""Google Sheets connector con soporte para OAuth y Service Account."""

import logging
import os
from pathlib import Path

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as OAuthCredentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
OAUTH_CREDENTIALS_FILE = "credentials.json"
OAUTH_TOKEN_FILE = "token.json"
SERVICE_ACCOUNT_FILE = "service_account.json"


def get_sheets_client() -> gspread.Client:
    """Get authenticated gspread client.

    Tries OAuth first (if credentials.json exists), falls back to service account.

    Returns:
        Authenticated gspread client

    Raises:
        FileNotFoundError: If neither OAuth nor service account credentials found
    """
    # Try OAuth first
    if Path(OAUTH_CREDENTIALS_FILE).exists():
        return _get_oauth_client()

    # Fallback to service account
    if Path(SERVICE_ACCOUNT_FILE).exists():
        return _get_service_account_client()

    raise FileNotFoundError(
        f"No credentials found. Need either {OAUTH_CREDENTIALS_FILE} or {SERVICE_ACCOUNT_FILE}"
    )


def _get_oauth_client() -> gspread.Client:
    """Get OAuth authenticated client."""
    creds = None

    # Load existing token if available
    if Path(OAUTH_TOKEN_FILE).exists():
        creds = OAuthCredentials.from_authorized_user_file(OAUTH_TOKEN_FILE, SCOPES)

    # If no valid credentials, log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired token
            creds.refresh(Request())
        else:
            # Full OAuth flow (opens browser)
            flow = InstalledAppFlow.from_client_secrets_file(
                OAUTH_CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save token for future runs with restrictive permissions
        token_path = Path(OAUTH_TOKEN_FILE)
        token_path.write_text(creds.to_json())

        # Set restrictive permissions (owner read/write only, 0o600)
        os.chmod(token_path, 0o600)
        logger.info(f"Token saved to {OAUTH_TOKEN_FILE} with restrictive permissions")

    return gspread.authorize(creds)


def _get_service_account_client() -> gspread.Client:
    """Get service account authenticated client."""
    creds = ServiceAccountCredentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return gspread.authorize(creds)


def get_worksheet(spreadsheet_id: str, sheet_name: str) -> gspread.Worksheet:
    """Get a specific worksheet from a spreadsheet.

    Args:
        spreadsheet_id: Google Spreadsheet ID
        sheet_name: Name of the worksheet

    Returns:
        gspread.Worksheet instance
    """
    client = get_sheets_client()
    return client.open_by_key(spreadsheet_id).worksheet(sheet_name)
