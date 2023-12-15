import os
import logging
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate_google_drive(script_directory):
    """
    Handles Google Drive authentication and token refresh.

    Parameters:
    script_directory (str): Directory where the token and credentials files are stored.
    """
    creds = None
    token_path = os.path.join(script_directory, 'token.json')
    credentials_path = os.path.join(script_directory, 'credentials.json')

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logging.error(f"Error refreshing Google Drive token: {e}")
                return None
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                logging.error(f"Error during Google Drive authentication: {e}")
                return None

        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return creds

if __name__ == '__main__':
    script_directory = os.path.dirname(__file__)
    authenticate_google_drive(script_directory)
