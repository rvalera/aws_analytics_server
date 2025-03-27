from fastapi import FastAPI
import os
from dotenv import load_dotenv
import boto3
from utils.s3 import S3Client
import redis
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

from services.file_processer import FileProcesser
from services.file_processer import FileProcesser

app = FastAPI()


load_dotenv()

TEMPDIR = os.getenv("TEMPDIR")

AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_S3_BASE_PATH = os.getenv("AWS_S3_BASE_PATH")

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")


executor = ThreadPoolExecutor()

# Initialize Redis client
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

def is_process_running():
    return redis_client.get('process_running') is not None

@app.get("/process_status")
def get_process_status():
    return {
        "is_running": is_process_running(),
        "started_at": redis_client.get('process_started_at').decode() if redis_client.get('process_started_at') else None
    }

async def process_files_async():
    try:

        process_files = FileProcesser(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,bucket_name=AWS_S3_BUCKET, s3_base_path=AWS_S3_BASE_PATH  ,local_directory=TEMPDIR)

        print(f'Processing Files')        
        process_files.execute()
            

    finally:
        redis_client.delete('process_running')
        redis_client.delete('process_started_at')

@app.post("/activate_process")
async def activate_process():
    if is_process_running():
        return {"error": "Process is already running"}

    # Set process status in Redis
    redis_client.set('process_running', '1')
    redis_client.set('process_started_at', datetime.now().isoformat())

    # Start async processing
    asyncio.create_task(process_files_async())
    
    return {"message": "Process started", "status": "running"} 


