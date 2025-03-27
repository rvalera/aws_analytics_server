import boto3
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import os
from botocore.exceptions import ClientError

class BedrockClaudeProcessor:

    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
    ):
        # Load environment variables
        
        load_dotenv()
        
        # Get values from .env file with defaults
        self.max_tokens = int(os.getenv('BEDROCK_MAX_TOKENS', '4096'))
        self.temperature = float(os.getenv('BEDROCK_TEMPERATURE', '1'))
        region_name = os.getenv('AWS_REGION', 'us-east-2')

        self.model_id = os.getenv('AWS_BEDROCK_MODEL_ID', 'us.anthropic.claude-3-7-sonnet-20250219-v1:0')
        self.antropic_version = os.getenv('ANTROPIC_VERSION', 'bedrock-2023-05-31') 

        self.prompt_file = os.getenv('PROMPT_FILE')
        self.prompt = ''
        if self.prompt_file:
            with open(self.prompt_file, 'r') as f:
                self.prompt = f.read()

        # Initialize Bedrock client with credentials
        self.bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )



    def __create_model_request(self,content_type :str, content_to_analyze: list[str]) -> Dict[str, Any]:
        user_messages = []  

        user_messages.append({ "type": "text", "text": self.prompt })
        
        if content_type == 'text':
            user_messages.append({ "type": "text", "text" : f' This text to Analyze: {content_to_analyze[0]}'   })
        elif content_type == 'image':
            for content in content_to_analyze:
                user_messages.append({ "type": "image", "source": { "type": "base64", "media_type": "image/png", "data": content } })

        native_request = {
            "anthropic_version": self.antropic_version,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {
                    "role": "user",
                    "content": user_messages
                }
            ],
        }

        return native_request
    
    def invoke_model(self, content_type: str, content_to_analyze: list[str]) -> Dict[str, Any]:

        model_request = self.__create_model_request(content_type, content_to_analyze)
        
        json_response = None

        try:

            definitive_request = json.dumps(model_request)

            # Invoke the model with the request.
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=definitive_request
            )

            if not response is None:
                # Decode the response body.
                model_response = json.loads(response["body"].read())
                
                # Extract and print the response text.
                response_text = model_response["content"][0]["text"]
                json_response = json.loads(response_text)

            else:
                print('Response is NONE')


        except (ClientError, Exception) as e:
            print(f"ERROR: Can't invoke '{self.model_id}'. Reason: {e}")

            
        return json_response if not json_response is None else {}

