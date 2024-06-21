from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta, timezone

class AzureBlobUploader:
    def __init__(self, account_name, account_key, container_name):
        self.account_name: str = account_name
        self.account_key: str = account_key
        self.container_name: str = container_name
        self.blob_service_client = BlobServiceClient(
            account_url=f"https://{self.account_name}.blob.core.windows.net",
            credential= self.account_key
        )
        self.container_client = self.blob_service_client.get_container_client(self.container_name)

        self.timezone_buenos_aires = timezone(timedelta(hours=-3))

    def upload_file(self, file, file_name: str):
        blob_client = self.container_client.get_blob_client(file_name)
        blob_client.upload_blob(file)
    
    def generate_file_url(self, file_name: str, expiry_hours: int = 1):
        expiry = datetime.now(self.timezone_buenos_aires) + timedelta(hours=expiry_hours)
        sas_token = generate_blob_sas(
            account_name=self.account_name,
            container_name=self.container_name,
            blob_name=file_name,
            account_key=self.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=expiry
        )
        file_url = f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{file_name}?{sas_token}"
        return file_url