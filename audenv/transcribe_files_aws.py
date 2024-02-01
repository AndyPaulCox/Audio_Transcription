import boto3
import time
import os
import datetime
import json
                
def list_files(bucket, prefix):
    s3_client = boto3.client('s3')
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    # Print the entire response for debugging
    print(f"Response from S3: {response}")
    if 'Contents' not in response or not response['Contents']:
        # Print a message if no files are found
        print(f"No files found in {bucket} with prefix '{prefix}'")
    else:
        for obj in response['Contents']:
            # Check if the object represents a file (not a folder)
            if obj['Size'] > 0:
                yield obj.get('Key')

def delete_unwanted_files(bucket, prefix):
    s3_client = boto3.client('s3')
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)

    if 'Contents' in response:
        for obj in response['Contents']:
            file_key = obj['Key']
            if file_key.startswith('._'):
                s3_client.delete_object(Bucket=bucket, Key=f'{prefix}/{file_key}')
                print(f"Deleted unwanted file: {file_key}")

def start_transcribe_job(s3_uri, job_name, output_bucket):
    transcribe_client = boto3.client('transcribe')
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    output_filename = f"transcript-{timestamp}.json"
    output_path = f"{output_bucket}"
    print(f"Initiating transcription job for file: {s3_uri} with job name: {job_name}")
    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': s3_uri},
        MediaFormat='mp3', # Change this depending on your file format
        LanguageCode='en-US', # Change this depending on your language
        OutputBucketName=output_path
    )

def check_job_status(job_name):
    """
    Check the status of a Amazon Transcribe job
    """
    transcribe_client = boto3.client('transcribe')
    response = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
    return response['TranscriptionJob']['TranscriptionJobStatus']

def delete_s3_object(bucket, key):
    """
    Delete a specific file in an S3 bucket
    """
    s3_client = boto3.client('s3')
    s3_client.delete_object(Bucket=bucket, Key=key)

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
    

def main():
    bucket_name = 'r-sample-69c534b4'
    input_prefix = 'Input/'

    while True:
        # Delete files starting with '._'
        delete_unwanted_files(bucket_name, input_prefix)
        for file_key in list_files(bucket_name, input_prefix):
            print(f"Processing file: {file_key}")
            s3_uri = f's3://{bucket_name}/{file_key}'
            print(f"Constructed S3 URI for the file: {s3_uri}")
            job_name = f"Transcribe_{os.path.basename(file_key)}_{int(time.time())}"
            print(f"Checking status for transcription job: {job_name}")
            start_transcribe_job(s3_uri, job_name, bucket_name)

            while True:
                status = check_job_status(job_name)
                print(f"Current status of job '{job_name}': {status}")
                if status in ['COMPLETED', 'FAILED']:
                    break
                time.sleep(30)  # Wait for 30 seconds before checking the status again

            if status == 'COMPLETED':
                print(f"Transcription job '{job_name}' completed successfully.")
                delete_s3_object(bucket_name, file_key)
                
                # List and process each JSON file in the output folder
        json_files = list_json_files(bucket_name)
        for json_file in json_files:
            print(f"Now processing json file: {json_file }")
            process_json_files(bucket_name) 
            
        time.sleep(60)  # Check for new files every minute 
        
             

if __name__ == '__main__':
    main()
