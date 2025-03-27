import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import os
from botocore.exceptions import ClientError

class S3Client:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

    def get_files(self, bucket_name,prefix):

        files  = []
        try:
            # bucket_name, prefix = bucket.replace("s3://", "").split("/", 1)
            
            response = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            files = [content['Key'] for content in response.get('Contents', [])]

        except NoCredentialsError:
            print("Credentials not available")
        except PartialCredentialsError:
            print("Incomplete credentials provided")

        return files

    def download_file(self, bucket_name: str, s3_path: str, local_path: str) -> bool:
        """
        Download a file from S3 to local filesystem
        
        Args:
            bucket_name (str): Name of the S3 bucket
            s3_path (str): Path to file in S3 bucket
            local_path (str): Local path where file will be saved
            
        Returns:
            bool: True if download was successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist 
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Download file from S3
            self.s3_client.download_file(bucket_name, s3_path, local_path)
            return True
            
        except ClientError as e:
            print(f"Error downloading file: {e}")
            return False    


    def move_file(self, bucket_name: str, source_s3_path: str, dest_s3_path: str) -> bool:
        """
        Move a file from one S3 path to another within the same bucket
        
        Args:
            bucket_name (str): Name of the S3 bucket
            source_path (str): Source path of file in S3
            dest_path (str): Destination path in S3
            
        Returns:
            bool: True if move was successful, False otherwise
        """
        try:
            # Copy object to new location
            self.s3_client.copy_object(
                Bucket=bucket_name,
                CopySource={'Bucket': bucket_name, 'Key': source_s3_path},
                Key=dest_s3_path
            )
            
            # Delete original object
            self.s3_client.delete_object(
                Bucket=bucket_name,
                Key=source_s3_path
            )
            return True
            
        except ClientError as e:
            print(f"Error moving file: {e}")
            return False

    def upload_file(self, local_path: str,  bucket_name: str, s3_path: str) -> bool:
        """
        Upload a file from local filesystem to S3
        
        Args:
            bucket_name (str): Name of the S3 bucket
            local_path (str): Local path of file to upload
            s3_path (str): Path in S3 bucket where file will be saved"
            """
        try:
            # Upload file to S3
            self.s3_client.upload_file(local_path, bucket_name, s3_path)
            return True
            
        except ClientError as e:
            print(f"Error uploading file: {e}")
            return False