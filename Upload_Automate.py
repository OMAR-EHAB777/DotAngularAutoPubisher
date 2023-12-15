#region
import os
import logging
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from Authenticate import SCOPES
#endregion
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def upload_to_drive(file_path, file_name, script_directory):
    """
    Uploads a file to Google Drive and returns its shareable link.

    Parameters:
    file_path (str): The path to the file to upload.
    file_name (str): The name to assign to the file on Google Drive.
    script_directory (str): The path to the directory where the token.json file is stored.

    Returns:
    str: The shareable link to the uploaded file on Google Drive.
    """
    creds = Credentials.from_authorized_user_file(
        os.path.join(script_directory, 'token.json'), SCOPES)
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': file_name}
    media = MediaFileUpload(file_path, mimetype='application/octet-stream', chunksize=1024*1024, resumable=True)
    request = service.files().create(body=file_metadata, media_body=media, fields='id')

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            logging.info("Uploaded %d%%." % (status.progress() * 100))

    file_id = response.get('id')
    logging.info(f"Uploaded file with ID: {file_id}")

    try:
        # Make the file public and get the shareable link
        permission_response = service.permissions().create(
            fileId=file_id,
            body={'type': 'anyone', 'role': 'reader'},
            fields='id'
        ).execute()

        # Verify permission change was successful
        if permission_response.get('id'):
            file_link = f"https://drive.google.com/uc?id={file_id}&export=download"
            logging.info(f"File link: {file_link}")
            return file_link
        else:
            logging.error("Failed to set file permissions.")
            return None
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None
