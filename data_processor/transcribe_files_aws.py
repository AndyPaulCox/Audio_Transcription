import boto3
import time
import os
import datetime
import json
import os
from data_processor import *
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
#from datetime import datetime
                
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

def delete_unwanted_files(bucket, prefix='', include_subdirectories=False):
    s3_client = boto3.client('s3')
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    print(f"FdelUF: Response from S3: {response}")
    if 'Contents' in response:
        for obj in response['Contents']:
            file_key = obj['Key']
            print(f"FdelUF: File key from S3: {file_key}")
            # Check if the file is in the top level or in a subdirectory based on slashes in the key
            #in_top_level = '/' not in file_key[len(prefix):].lstrip('/')
            if file_key.startswith('.'):
                s3_client.delete_object(Bucket=bucket, Key=file_key)
                print(f"FdelUF: Deleted unwanted file: {file_key}")
                
        #s3_client = boto3.client('s3')
        # Ensure folder name ends with a '/'
        prefix = 'Input'
        # Continuously fetch objects and delete them until all are removed
        while True:
            # List objects within the specified folder
            response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        
            # Check if there are contents to delete
            if 'Contents' not in response:
                print("No more files to delete.")
                break

            # Filter and delete each object that starts with '.'
            for obj in response['Contents']:
                file_key = obj['Key']
                if file_key.split('/')[-1].startswith('.'):
                    s3_client.delete_object(Bucket=bucket, Key=file_key)
                    print(f"Deleted: {file_key}")

            # Check if the response is truncated, indicating more objects to fetch
            if not response.get('IsTruncated'):
                break  # Exit loop if no more objects to list

def start_transcribe_job(s3_uri, job_name, output_bucket):
    transcribe_client = boto3.client('transcribe')
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    output_filename = f"transcript-{timestamp}.json"
    output_path = f"{output_bucket}"
    print(f"Initiating transcription job for file: {s3_uri} with job name: {job_name}")
    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': s3_uri},
        MediaFormat='wav', # Change this depending on your file format
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
    
def summarize_text(text):
    """Send text to OpenAI's ChatGPT for summarization using the updated API syntax."""
    response = client.chat.completions.create(model="gpt-4",  # Updated to use a supported model, e.g., "gpt-3.5-turbo"
    messages=[
        {"role": "system", "content": "You are an expert project manager."},
        {"role": "user", "content": f"Please produce a summary ofthe following text and add a section noting any action points:\n\n{text}"}
    ])
    print("completed Summarization")
    return response.choices[0].message.content.strip()

def timestamp_text(text):
    """Append a timestamp to the text."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{text}\n\nTimestamp: {timestamp}"

def process_text_file(file_path):
    """Process a text file to summarize and timestamp its content."""
    with open(file_path, 'r') as file:
        text = file.read()
    print("Reading meeting transcription:{file_path}")
    summarized_text = summarize_text(text)
    timestamped_summary = timestamp_text(summarized_text)

    # Save the summarized and timestamped text to a new file
    print("Saving meeting summary:{file_path}")
    output_file_path = file_path.replace('.txt', '_summarized.txt')
    with open(output_file_path, 'w') as file:
        file.write(timestamped_summary)
    print(f"Summarized text saved to: {output_file_path}")

def main():
    bucket_name = 'r-sample-69c534b4'
    input_prefix = 'Input/'
    directory = '/Users/apcox/AWS_S3/'  # Update this path to your specific directory
    
    while True:
        # Delete files starting with '._'
        delete_unwanted_files(bucket_name,include_subdirectories=False)
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
            delete_s3_object(bucket_name, json_file)
        # Now do the summary ond action points
        
        for filename in os.listdir(directory):
            if filename.endswith('.txt'):
                file_path = os.path.join(directory, filename)
                process_text_file(file_path)
            
        time.sleep(60)  # Check for new files every minute 
        
    delete_unwanted_files(bucket_name,include_subdirectories=False)
        
if __name__ == '__main__':
    main()
