import datetime
import time
import os
from data_processor import *


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