import boto3
import datetime
import json
import os

def list_json_files(bucket):
    """List JSON files in the specified S3 bucket and prefix."""
    s3_client = boto3.client('s3')
    response = s3_client.list_objects_v2(Bucket=bucket)
    return [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.json')]

def process_json_files(s3_bucket):
    """Process all JSON files in a specified folder in an S3 bucket."""
    s3_client = boto3.client('s3')

    # List all files in the specified folder
    response = s3_client.list_objects_v2(Bucket=s3_bucket)
    if 'Contents' in response:
        for file in response['Contents']:
            file_key = file['Key']

            # Process each JSON file
            if file_key.endswith('.json'):
                print(f"Now extracting from json file: {file}")
                # Download the JSON file from S3
                json_file_response = s3_client.get_object(Bucket=s3_bucket, Key=file_key)
                json_content = json_file_response['Body'].read().decode('utf-8')
                transcription_data = json.loads(json_content)

                # Extract the transcript text
                transcript_text = transcription_data['results']['transcripts'][0]['transcript']

                # Generate a timestamped filename for the txt file
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                txt_file_name = f"transcript_{timestamp}.txt"
                
                # Define the path to the mounted S3 bucket
                mounted_s3_path = "/Users/apcox/"
                output_prefix = "AWS_S3/"

                # Generate the full file path where the transcript will be saved
                full_file_path = os.path.join(mounted_s3_path, output_prefix, txt_file_name)

                # Write the transcript to a .txt file in the mounted S3 path
                with open(full_file_path, 'w') as txt_file:
                    txt_file.write(transcript_text)
                

    # Handle the case where no files are found
    else:
        print("No files found in the specified folder.")
    