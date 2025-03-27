import os
from typing import List
from utils.s3 import S3Client
from utils.pdf import PDFProcessor  
from utils.bedrock import BedrockClaudeProcessor

from time import sleep

import json

class FileProcesser:

    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, bucket_name: str, s3_base_path: str, local_directory: str):
        self.s3_client = S3Client(aws_access_key_id, aws_secret_access_key, "us-east-2")
        self.bedrock_claude_processor = BedrockClaudeProcessor(aws_access_key_id, aws_secret_access_key)

        self.bucket_name = bucket_name
        self.local_directory = local_directory
        self.s3_base_path = s3_base_path    
        self.local_directory = local_directory

        self.s3_incoming_path = os.path.join(s3_base_path, "incoming")
        self.local_incoming_path = os.path.join(local_directory, "incoming")

        self.s3_results_path = os.path.join(s3_base_path, "results")
        self.local_results_path = os.path.join(local_directory, "results")

        self.s3_processed_path = os.path.join(s3_base_path, "processed")
        self.local_processed_path = os.path.join(local_directory, "processed")

        self.s3_error_path = os.path.join(s3_base_path, "error")
        self.local_error_path = os.path.join(local_directory, "error")


        print(f'INCOMING PATH: {self.s3_incoming_path}')
        print(f'LOCAL INCOMING PATH: {self.local_incoming_path}')

        print(f'RESULTS PATH: {self.s3_results_path}')
        print(f'LOCAL RESULTS PATH: {self.local_results_path}')

        print(f'PROCESSED PATH: {self.s3_processed_path}')
        print(f'LOCAL PROCESSED PATH: {self.local_processed_path}')

        print(f'ERROR PATH: {self.s3_error_path}')
        print(f'LOCAL ERROR PATH: {self.local_error_path}')


    def __download_files_from_bucket(self) -> List[str]:
        # Ensure local directory exists
        os.makedirs(self.local_incoming_path, exist_ok=True)
        
        # Get list of files from bucket
        files = self.s3_client.get_files(self.bucket_name, self.s3_incoming_path)
        print(f'S3 Files: {files}')    

        downloaded_files = []

        # Download each file
        for file_key in files:
            only_filename, extension = os.path.splitext(file_key)
            if extension in ('.pdf', '.png'):
                local_file_path = os.path.join(self.local_incoming_path, os.path.basename(file_key))
                self.s3_client.download_file(self.bucket_name, file_key, local_file_path)
                downloaded_files.append(local_file_path)

        return downloaded_files
    
    def __store_results(self, file: str, results: dict):
        try:
            if len(results) > 0: 
                print(f"Moving file to processed: {file}")
                os.rename(file, os.path.join(self.local_processed_path, os.path.basename(file)))
                self.s3_client.move_file(self.bucket_name, os.path.join(self.s3_incoming_path, os.path.basename(file)), os.path.join(self.s3_processed_path, os.path.basename(file)))

                results_filename = os.path.splitext(os.path.basename(file))[0] + '.json'
                results_path = os.path.join(self.local_results_path, results_filename)
                os.makedirs(self.local_results_path, exist_ok=True)
                with open(results_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=4)

                self.s3_client.upload_file(results_path,self.bucket_name, os.path.join(self.s3_results_path, results_filename))
            else:
                print(f"Moving file to error: {file}")
                os.rename(file, os.path.join(self.local_error_path, os.path.basename(file)))

                self.s3_client.move_file(self.bucket_name, os.path.join(self.s3_incoming_path, os.path.basename(file)), os.path.join(self.s3_error_path, os.path.basename(file)))        
        except Exception as e:
            print(f"Error storing results: {e}")


    
    def execute(self):
        local_files = self.__download_files_from_bucket()
        for file in local_files:
            print(f"Processing file: {file}")
            
            pdf_processor = PDFProcessor(file)
            contentype, content = pdf_processor.get_content_to_analyze()
            print(f'Content Type: {contentype}')
            print(f'Content Length: {len(content)}')

            results = self.bedrock_claude_processor.invoke_model(contentype, content)
            self.__store_results(file, results)
            
            sleep(20)
            # break


        print(f'Files Processed: {local_files}')

