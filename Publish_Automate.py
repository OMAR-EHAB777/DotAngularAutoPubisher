#region Import
import logging
from pathlib import Path
import subprocess
import os
import shutil
from datetime import datetime
import sys
from Email_Automate import send_email
from Upload_Automate import upload_to_drive 
#endregion

#region Set up logging
logging.basicConfig(filename='publish_automate.log', level=logging.INFO,
        format='%(asctime)s:%(levelname)s:%(message)s')
#endregion

#region Get the current date
current_date = datetime.now().strftime("%Y-%m-%d")
#endregion

#region Define project settings for .NET backend
script_directory = os.path.dirname(__file__)
if not script_directory:
    script_directory = os.getcwd()
#endregion
    
#region Define project settings for .Net Backend
backend_project_path = os.path.join(Path(script_directory).parent, "POS_BackEnd", "POS.Web")
backend_publish_output_path = os.path.join(Path(script_directory).parent, f"Pos-Back-{current_date}")
backend_rar_output_path = os.path.join(Path(script_directory).parent, f"Pos-Back-{current_date}.rar")
backend_repo_path =os.path.join(Path(script_directory).parent, "POS_BackEnd")
mongo_dump_path =os.path.join(script_directory, "mongodump.exe")


#endregion

#region Define project settings for Angular frontend
frontend_project_path = os.path.join(Path(script_directory).parent, "Front", "POSFront")
frontend_build_output_path = os.path.join(frontend_project_path, "dist")
frontend_publish_output_path = os.path.join(Path(script_directory).parent, f"Pos-Front-{current_date}")
frontend_rar_output_path = os.path.join(Path(script_directory).parent, f"Pos-Front-{current_date}.rar")
frontend_repo_path =os.path.join(Path(script_directory).parent, "Front", "POSFront")
web_config_path = os.path.join(script_directory, "web.config")
#endregion


#region Define the path to the Angular app's output directory (adjust the 'POS' as necessary to match your app's output folder name)
angular_app_output_path = os.path.join(frontend_publish_output_path, "POS")
#endregion

#region Define the full path to the Node.js executable
node_path = "C:\\Program Files\\nodejs\\node.exe"
ng_cli_path = os.path.join("C:\\Users\\MahmoudMohee\\AppData\\Roaming\\npm\\node_modules\\@angular\\cli\\bin\\ng")
#endregion

#region Path to WinRAR executable
winrar_path = "C:\\Program Files\\WinRAR\\WinRAR.exe"
#endregion

#region clear exist published with same date
def clear_directory(dir_path):
    if os.path.isdir(dir_path):
        shutil.rmtree(dir_path)

def clear_file(file_path):
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
    except OSError as e:
        print(f"Error deleting file {file_path}: {e.strerror}")
#endregion
#region pull recents before publish
def pull_latest_changes(repo_path):
    """
    Pulls the latest changes from the master branch of the given repository.
    """
    try:
        # Change directory to the repo
        os.chdir(repo_path)
        # Pull the latest changes from the master branch
        subprocess.run(['git', 'checkout', 'master'], check=True)
        subprocess.run(['git', 'pull', 'origin', 'master'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to pull latest changes in {repo_path}: {e}")
        sys.exit(1)

# Before publishing, pull the latest changes for the backend
pull_latest_changes(backend_repo_path)
# Before building, pull the latest changes for the frontend
pull_latest_changes(frontend_repo_path)
#endregion

#region publishing
# Step 1: Publish the .NET backend web app
try:
    os.chdir(backend_project_path)
    subprocess.run(["dotnet", "publish", "-c", "Release", "-o", backend_publish_output_path], check=True)

#Step 2: Build the Angular frontend app
    os.chdir(frontend_project_path)
    subprocess.run([node_path, ng_cli_path, "build", "--prod"], check=True)
except subprocess.CalledProcessError as e:
    logging.error(f"An error occurred while running a command: {e}")
    # Handle the error or re-raise
    raise
except Exception as e:
    logging.error(f"An unexpected error occurred: {e}")
    # Handle the error or re-raise
    raise
#endregion

#region Step 3: Copy Angular build output to publish directory
clear_directory(frontend_publish_output_path)
shutil.copytree(frontend_build_output_path, frontend_publish_output_path)
#endregion

#region Step 4: Copy web.config to Angular app's output directory inside the publish directory
shutil.copy(web_config_path, angular_app_output_path)
#endregion
#region Step 4: Copy mongodump to backend
# app's output directory inside the publish directory
shutil.copy(mongo_dump_path, backend_rar_output_path)
#endregion
#region Step 5: Compress the published .NET backend app to .rar
clear_file(backend_rar_output_path)
os.makedirs(os.path.dirname(backend_rar_output_path), exist_ok=True)
subprocess.run([winrar_path, "a", "-r", backend_rar_output_path, backend_publish_output_path], check=True)
#endregion

#region Step 6: Compress the published Angular frontend app to .rar
clear_file(frontend_rar_output_path) 
os.makedirs(os.path.dirname(frontend_rar_output_path), exist_ok=True)
subprocess.run([winrar_path, "a", "-r", frontend_rar_output_path, frontend_publish_output_path], check=True)
#endregion

#region Call the upload function
backend_link =upload_to_drive(backend_rar_output_path, os.path.basename(backend_rar_output_path), script_directory)
frontend_link =upload_to_drive(frontend_rar_output_path, os.path.basename(frontend_rar_output_path), script_directory)
print("Upload to Google Drive completed.")
print("Backend and frontend publishing, file copying, compression, and uploading completed successfully.")
#endregion


#region Prepare the email content
print("Start Sending Emails.")
subject = "New Pos Release !!!"
recipient_emails = ["omarehabdev@gmail.com",
                    "ahmadsamirnabil@gmail.com","Amrragaay1995@outlook.com"
                    ,"ysmaher@gmail.com"
                    ,"Mahmoodkarman@yahoo.com",
                    "mostafaatef6066@gmail.com"]  # List of recipient email addresses
sender = "ferpbooking@gmail.com"  # Your Gmail address
sender_password = "ecby njar xpdf cynt"  # Your Gmail password or app password

image_path = os.path.join(script_directory,"newRelease.gif") # Path to your image
html_body = f"""
<html>
  <body>
    <p>Here are the links to the uploaded files:</p>
    <p>Backend: <a href="{backend_link}">{backend_link}</a></p>
    <p>Frontend: <a href="{frontend_link}">{frontend_link}</a></p>
    <p><img src="cid:newRelease" alt="New Release" /></p>
  </body>
</html>
"""
# Send the email
send_email(subject, html_body, recipient_emails, sender, sender_password, image_path)

print("Email sent successfully.")
#endregion

if __name__ == "__main__":
    # Call your main functions here if needed
    pass