import boto3
import os
import requests
from dotenv import load_dotenv

load_dotenv('.env')

AWS_ACCESS_KEY_ID : str = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')

site_id = os.getenv('site_id')
drive_id = os.getenv('drive_id')

client_id = os.getenv('client_id')
client_secret = os.getenv('client_secret')
tenant_id = os.getenv('tenant_id')

s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_REGION)

BUCKET_NAME =os.getenv('BUCKET_NAME')
folder ='Europa'


objects = s3.list_objects_v2(Bucket=BUCKET_NAME)['Contents']

def get_access_token():
    auth_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }
    response = requests.post(auth_url, data=data)
    return response.json()['access_token']

# Upload each file to SharePoint
access_token = get_access_token()

for obj in objects:
    file_name = obj['Key']
    local_file_path = os.path.basename(file_name)  
    print("local_file_path :", local_file_path)
    
    s3.download_file(BUCKET_NAME, file_name, local_file_path)
    
    # Upload the file to SharePoint
    upload_url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/root:/{folder}/{file_name}:/content'
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/octet-stream',
        'Content-Length': str(os.path.getsize(local_file_path))
    }
    
    with open(local_file_path, 'rb') as file:
        response = requests.put(upload_url, headers=headers, data=file)
        print(f"Uploaded {file_name}: {response.json()}")
    
    # Remove the downloaded file
    os.remove(local_file_path)

print("Uploaded to SharePoint successfully!")
